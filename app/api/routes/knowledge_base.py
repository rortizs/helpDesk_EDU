from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models import User
from app.schemas.articles import ArticleIn
from app.services.articles import ArticleService

router = APIRouter()


@router.get("/api/knowledge-base")
def articles(q: str | None = None, db: Session = Depends(get_db)) -> list[dict]:
    return ArticleService(db).list(q)


@router.post("/api/knowledge-base", status_code=201)
def article(body: ArticleIn, user: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    return ArticleService(db).create(body, user)


@router.get("/api/knowledge-base/{article_id}")
def article_detail(article_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    return ArticleService(db).detail(article_id)


@router.patch("/api/knowledge-base/{article_id}")
def edit_article(article_id: int, body: ArticleIn, _: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    return ArticleService(db).update(article_id, body)


@router.delete("/api/knowledge-base/{article_id}", status_code=204)
def delete_article(article_id: int, _: Annotated[User, Depends(require_roles("supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> None:
    ArticleService(db).delete(article_id)
