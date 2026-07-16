from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user, require_roles
from app.models import User
from app.schemas.tickets import AssignIn, CommentIn, StatusIn, TicketIn
from app.services.tickets import TicketService

router = APIRouter()


@router.post("/api/tickets", status_code=201)
def create_ticket(body: TicketIn, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).create(body, user)


@router.get("/api/tickets")
def list_tickets(status_filter: str | None = None, category: str | None = None, priority: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    return TicketService(db).list(user, status_filter, category, priority)


@router.get("/api/tickets/{ticket_id}")
def detail(ticket_id: int, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).detail(ticket_id, user)


@router.get("/api/tickets/{ticket_id}/history")
def history(ticket_id: int, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).history(ticket_id, user)


@router.patch("/api/tickets/{ticket_id}")
def update(ticket_id: int, body: TicketIn, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).update(ticket_id, body, user)


@router.patch("/api/tickets/{ticket_id}/assign")
def assign(ticket_id: int, body: AssignIn, user: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).assign(ticket_id, body, user)


@router.patch("/api/tickets/{ticket_id}/status")
def change_status(ticket_id: int, body: StatusIn, user: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).change_status(ticket_id, body, user)


@router.post("/api/tickets/{ticket_id}/cancel")
def cancel(ticket_id: int, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).cancel(ticket_id, user)


@router.post("/api/tickets/{ticket_id}/close")
def close(ticket_id: int, user: Annotated[User, Depends(require_roles("technician", "supervisor", "administrator"))], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).close(ticket_id, user)


@router.post("/api/tickets/{ticket_id}/comments", status_code=201)
def comment(ticket_id: int, body: CommentIn, user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).comment(ticket_id, body, user)


@router.get("/api/dashboard")
def dashboard(user: Annotated[User, Depends(current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    return TicketService(db).dashboard(user)
