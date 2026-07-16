"""Database setup shared by the app factory and request dependencies."""
from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Base class for all persistence models."""


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    options: dict = {}
    if database_url.startswith("sqlite"):
        options = {"connect_args": {"check_same_thread": False}}
        if database_url == "sqlite://":
            options["poolclass"] = StaticPool
    engine = create_engine(database_url, **options)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def get_db(request: Request) -> Generator[Session, None, None]:
    """Yield one session from the factory installed by ``create_app``."""
    db = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()
