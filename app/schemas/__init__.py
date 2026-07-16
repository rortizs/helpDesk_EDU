"""Request DTOs grouped by use case."""
from app.schemas.articles import ArticleIn
from app.schemas.auth import Login
from app.schemas.tickets import AssignIn, CommentIn, StatusIn, TicketIn

__all__ = ["ArticleIn", "AssignIn", "CommentIn", "Login", "StatusIn", "TicketIn"]
