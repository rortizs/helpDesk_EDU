"""FastAPI composition root: construct infrastructure and register adapters."""
from fastapi import FastAPI

from app.api.routes import assistance, auth, knowledge_base, mobile, notifications, system, tickets, users
from app.core.config import settings
from app.core.database import create_session_factory
from app.services.auth import seed_users
from app.web import routes as web_routes


def create_app(database_url: str | None = None) -> FastAPI:
    """Create an isolated app so tests can provide a fresh SQLite database."""
    app = FastAPI(title="HelpDesk EDU")
    app.state.session_factory = create_session_factory(database_url or settings.database_url)
    with app.state.session_factory() as db:
        seed_users(db)

    for router in (system.router, auth.router, users.router, tickets.router, notifications.router, mobile.router, assistance.router, knowledge_base.router, web_routes.router):
        app.include_router(router)
    return app


app = create_app()
