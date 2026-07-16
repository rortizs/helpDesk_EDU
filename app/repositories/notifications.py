from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def for_user(self, user_id: int) -> list[Notification]:
        return list(self.db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.id.desc())).all())

    def owned_by(self, notification_id: int, user_id: int) -> Notification | None:
        return self.db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))

    def unread_count(self, user_id: int) -> int:
        return int(self.db.scalar(select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.read_at.is_(None))) or 0)

    def commit(self) -> None:
        self.db.commit()