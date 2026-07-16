from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Notification, Ticket, User
from app.repositories.notifications import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.notifications = NotificationRepository(db)

    @staticmethod
    def serialize(item: Notification) -> dict:
        return {"id": item.id, "ticket_id": item.ticket_id, "title": item.title, "message": item.message, "channel": item.channel, "type": item.type, "read_at": item.read_at, "created_at": item.created_at}

    def create(self, user_id: int, ticket: Ticket, title: str, message: str, type: str) -> None:
        self.notifications.add(Notification(user_id=user_id, ticket_id=ticket.id, title=title, message=message, type=type))

    def notify_participants(self, ticket: Ticket, actor: User, title: str, message: str, type: str) -> None:
        for participant_id in {ticket.requester_id, ticket.assignee_id} - {None, actor.id}:
            self.create(participant_id, ticket, title, message, type)

    def list(self, user: User) -> dict:
        return {"items": [self.serialize(item) for item in self.notifications.for_user(user.id)], "unread_count": self.notifications.unread_count(user.id)}

    def unread_count(self, user: User) -> dict:
        return {"unread_count": self.notifications.unread_count(user.id)}

    def mark_read(self, notification_id: int, user: User) -> dict:
        item = self.notifications.owned_by(notification_id, user.id)
        if not item:
            raise HTTPException(404, "Notification not found")
        if item.read_at is None:
            item.read_at = datetime.utcnow()
            self.notifications.commit()
        return self.serialize(item)