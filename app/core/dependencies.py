"""Reusable authentication and role dependencies for route adapters."""
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.repositories.users import UserRepository

bearer = HTTPBearer(auto_error=False)


def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], db: Annotated[Session, Depends(get_db)]) -> User:
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try:
        email = decode_access_token(credentials.credentials)["sub"]
    except (KeyError, ValueError):
        raise HTTPException(401, "Invalid token")
    user = UserRepository(db).by_email(email)
    if not user:
        raise HTTPException(401, "Unknown user")
    return user


def require_roles(*roles: str) -> Callable:
    def check(user: Annotated[User, Depends(current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(403, "Insufficient role")
        return user
    return check
