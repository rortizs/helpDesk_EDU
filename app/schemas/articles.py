from pydantic import BaseModel


class ArticleIn(BaseModel):
    title: str
    body: str
    category: str = "General"
