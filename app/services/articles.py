from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Article, User
from app.repositories.articles import ArticleRepository
from app.schemas.articles import ArticleIn


class ArticleService:
    def __init__(self, db: Session):
        self.articles = ArticleRepository(db)

    @staticmethod
    def serialize(article: Article) -> dict:
        return {"id": article.id, "title": article.title, "body": article.body, "category": article.category}

    def list(self, query: str | None) -> list[dict]:
        return [self.serialize(article) for article in self.articles.list(query)]

    def detail(self, article_id: int) -> dict:
        article = self.articles.by_id(article_id)
        if not article:
            raise HTTPException(404, "Article not found")
        return self.serialize(article)

    def create(self, body: ArticleIn, user: User) -> dict:
        return self.serialize(self.articles.add(Article(**body.model_dump(), author_id=user.id)))

    def update(self, article_id: int, body: ArticleIn) -> dict:
        article = self.articles.by_id(article_id)
        if not article:
            raise HTTPException(404, "Article not found")
        for field, value in body.model_dump().items():
            setattr(article, field, value)
        self.articles.commit()
        return self.serialize(article)

    def delete(self, article_id: int) -> None:
        article = self.articles.by_id(article_id)
        if not article:
            raise HTTPException(404, "Article not found")
        self.articles.delete(article)
