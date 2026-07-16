"""HTTP JSON adapters grouped by resource."""
from app.api.routes import auth, knowledge_base, system, tickets, users

__all__ = ["auth", "knowledge_base", "system", "tickets", "users"]
