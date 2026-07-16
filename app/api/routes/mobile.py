from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.models import User
from app.schemas.mobile import MobileMeOut, MobileTicketCreate, MobileTicketDetailOut, MobileTicketListOut, MobileTicketOut
from app.services.tickets import TicketService

router = APIRouter(prefix="/api/mobile", tags=["mobile"])


def compact(ticket: dict) -> dict:
    return {key: ticket[key] for key in ("id", "title", "status", "priority", "category")}


@router.get("/me", response_model=MobileMeOut)
def me(user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    tickets = TicketService(db).my_tickets(user)["items"]
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "open_ticket_count": sum(item["status"] not in ("Closed", "Cancelled") for item in tickets)}


@router.get("/tickets", response_model=MobileTicketListOut)
def my_tickets(user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return {"items": [compact(ticket) for ticket in TicketService(db).my_tickets(user)["items"]]}


@router.get("/tickets/{ticket_id}", response_model=MobileTicketDetailOut)
def ticket_detail(ticket_id: int, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    ticket = TicketService(db).detail(ticket_id, user)
    return {key: ticket[key] for key in ("id", "title", "status", "priority", "category", "description", "requester_id", "assignee_id", "created_at", "due_at")}


@router.post("/tickets", status_code=201, response_model=MobileTicketDetailOut)
def create_ticket(body: MobileTicketCreate, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    ticket = TicketService(db).create(body, user)
    return {key: ticket[key] for key in ("id", "title", "status", "priority", "category", "description", "requester_id", "assignee_id", "created_at", "due_at")}