from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user, require_roles
from app.models import User
from app.repositories.users import UserRepository

router = APIRouter()


@router.get("/api/users/me")
def me(user: Annotated[User, Depends(current_user)]) -> dict:
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@router.get("/api/users")
def users(_: Annotated[User, Depends(require_roles("administrator", "supervisor"))], db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return [{"id": user.id, "email": user.email, "name": user.name, "role": user.role} for user in UserRepository(db).all()]


@router.get("/api/catalogs")
def catalogs(_: Annotated[User, Depends(current_user)]) -> dict:
    return {"categories": ["General", "Hardware", "Software", "Network"], "priorities": ["Low", "Medium", "High", "Critical"], "statuses": ["Open", "In Progress", "Resolved", "Closed", "Cancelled"]}
