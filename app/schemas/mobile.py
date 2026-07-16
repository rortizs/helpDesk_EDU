from datetime import datetime

from pydantic import BaseModel

from app.schemas.tickets import TicketIn


class MobileMeOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    open_ticket_count: int


class MobileTicketOut(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    category: str


class MobileTicketDetailOut(MobileTicketOut):
    description: str
    requester_id: int
    assignee_id: int | None
    created_at: datetime
    due_at: datetime


class MobileTicketListOut(BaseModel):
    items: list[MobileTicketOut]


MobileTicketCreate = TicketIn