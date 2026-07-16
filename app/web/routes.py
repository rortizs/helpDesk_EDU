"""Server-rendered page adapters; templates and page URLs remain unchanged."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"title": "Login"})


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"title": "Dashboard"})


@router.get("/tickets", response_class=HTMLResponse)
def tickets_page(request: Request):
    return templates.TemplateResponse(request, "tickets.html", {"title": "Tickets"})


@router.get("/tickets/new", response_class=HTMLResponse)
def ticket_new(request: Request):
    return templates.TemplateResponse(request, "ticket_form.html", {"title": "New ticket"})


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_page(ticket_id: int, request: Request):
    return templates.TemplateResponse(request, "ticket_detail.html", {"title": "Ticket detail", "ticket_id": ticket_id})


@router.get("/knowledge-base", response_class=HTMLResponse)
def kb_page(request: Request):
    return templates.TemplateResponse(request, "knowledge_base.html", {"title": "Knowledge base"})


@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(request: Request):
    return templates.TemplateResponse(request, "notifications.html", {"title": "Notifications"})
