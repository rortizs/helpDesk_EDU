from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Login
from app.services.auth import AuthService

router = APIRouter()


@router.post("/api/auth/login")
def login(body: Login, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    user = AuthService(db).authenticate(body.email, body.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return AuthService(db).token_for(user)
