from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    ticket_id: int | None
    title: str
    message: str
    channel: str
    type: str
    read_at: datetime | None
    created_at: datetime


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    unread_count: int


class UnreadCountOut(BaseModel):
    unread_count: int