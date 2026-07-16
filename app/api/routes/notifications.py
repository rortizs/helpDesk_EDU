from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.models import User
from app.schemas.notifications import NotificationListOut, NotificationOut, UnreadCountOut
from app.services.notifications import NotificationService

router = APIRouter()


@router.get("/api/notifications", response_model=NotificationListOut)
def list_notifications(user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return NotificationService(db).list(user)


@router.get("/api/notifications/unread-count", response_model=UnreadCountOut)
def unread_count(user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return NotificationService(db).unread_count(user)


@router.post("/api/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return NotificationService(db).mark_read(notification_id, user)