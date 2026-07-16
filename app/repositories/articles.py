from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, query_text: str | None = None) -> list[Article]:
        query = select(Article)
        if query_text:
            query = query.where(Article.title.contains(query_text) | Article.body.contains(query_text))
        return list(self.db.scalars(query).all())

    def by_id(self, article_id: int) -> Article | None:
        return self.db.get(Article, article_id)

    def add(self, article: Article) -> Article:
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def commit(self) -> None:
        self.db.commit()

    def delete(self, article: Article) -> None:
        self.db.delete(article)
        self.db.commit()
