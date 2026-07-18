"""Server-rendered customer portal and protected staff workspace adapters."""
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.security import decode_access_token
from app.repositories.users import UserRepository
from app.schemas.tickets import TicketIn
from app.services.auth import AuthService
from app.services.tickets import TicketService

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")
STAFF_ROLES = {"technician", "supervisor", "administrator"}


def _current_web_user(request: Request):
    token = request.cookies.get("helpdesk_token")
    if not token:
        return None
    try:
        email = decode_access_token(token)["sub"]
    except (KeyError, ValueError):
        return None
    with request.app.state.session_factory() as db:
        return UserRepository(db).by_email(email)


def _customer_or_login(request: Request):
    user = _current_web_user(request)
    if user is None:
        return None
    if user.role != "requester":
        raise HTTPException(status_code=403, detail="The customer portal is only available to requesters")
    return user


def _staff_web_user(request: Request):
    user = _current_web_user(request)
    return user if user and user.role in STAFF_ROLES else None


def _staff_login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"title": "Login", "error": None})


@router.post("/login")
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    with request.app.state.session_factory() as db:
        user = AuthService(db).authenticate(email, password)
        if user is None:
            return templates.TemplateResponse(request, "login.html", {"title": "Login", "error": "Invalid credentials"}, status_code=401)
        token = AuthService(db).token_for(user)["access_token"]
    destination = "/portal" if user.role == "requester" else "/workspace"
    response = RedirectResponse(url=destination, status_code=303)
    response.set_cookie("helpdesk_token", token, httponly=True, samesite="lax")
    return response


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"title": "HelpDesk EDU", "user": _current_web_user(request)})


@router.post("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("helpdesk_token")
    return response


@router.get("/workspace", response_class=HTMLResponse)
def workspace(request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    return templates.TemplateResponse(request, "workspace.html", {"title": "Operations workspace", "user": user})


@router.get("/portal", response_class=HTMLResponse)
def customer_portal(request: Request):
    user = _customer_or_login(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    with request.app.state.session_factory() as db:
        tickets = TicketService(db).list(user, None, None, None)["items"]
    return templates.TemplateResponse(request, "portal.html", {"title": "Customer portal", "user": user, "tickets": tickets})


@router.get("/portal/tickets", response_class=HTMLResponse)
def customer_tickets(request: Request):
    user = _customer_or_login(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    with request.app.state.session_factory() as db:
        tickets = TicketService(db).list(user, None, None, None)["items"]
    return templates.TemplateResponse(request, "portal_tickets.html", {"title": "My tickets", "user": user, "tickets": tickets})


@router.get("/portal/tickets/new", response_class=HTMLResponse)
def customer_ticket_new(request: Request):
    user = _customer_or_login(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "portal_ticket_form.html", {"title": "Open a ticket", "user": user})


@router.post("/portal/tickets/new")
def customer_ticket_create(request: Request, title: str = Form(...), description: str = Form(...), category: str = Form("General"), priority: str = Form("Medium")):
    user = _customer_or_login(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    with request.app.state.session_factory() as db:
        ticket = TicketService(db).create(TicketIn(title=title, description=description, category=category, priority=priority), user)
    return RedirectResponse(url=f"/portal/tickets/{ticket['id']}", status_code=303)


@router.get("/portal/tickets/{ticket_id}", response_class=HTMLResponse)
def customer_ticket_detail(ticket_id: int, request: Request):
    user = _customer_or_login(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    with request.app.state.session_factory() as db:
        ticket = TicketService(db).detail(ticket_id, user)
    return templates.TemplateResponse(request, "ticket_detail.html", {"title": "Ticket detail", "ticket_id": ticket_id, "ticket": ticket, "user": user, "portal": True})


@router.get("/tickets", response_class=HTMLResponse)
def tickets_page(request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    with request.app.state.session_factory() as db:
        tickets = TicketService(db).list(user, None, None, None)["items"]
    return templates.TemplateResponse(request, "tickets.html", {"title": "Tickets", "user": user, "tickets": tickets})


@router.get("/tickets/new", response_class=HTMLResponse)
def ticket_new(request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    return templates.TemplateResponse(request, "ticket_form.html", {"title": "New ticket", "user": user})


@router.post("/tickets/new")
def ticket_create(request: Request, title: str = Form(...), description: str = Form(...), category: str = Form("General"), priority: str = Form("Medium")):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    with request.app.state.session_factory() as db:
        ticket = TicketService(db).create(TicketIn(title=title, description=description, category=category, priority=priority), user)
    return RedirectResponse(url=f"/tickets/{ticket['id']}", status_code=303)


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_page(ticket_id: int, request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    with request.app.state.session_factory() as db:
        try:
            ticket = TicketService(db).detail(ticket_id, user)
        except HTTPException:
            ticket = None
    return templates.TemplateResponse(request, "ticket_detail.html", {"title": "Ticket detail", "ticket_id": ticket_id, "ticket": ticket, "user": user})


@router.get("/knowledge-base", response_class=HTMLResponse)
def kb_page(request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    return templates.TemplateResponse(request, "knowledge_base.html", {"title": "Knowledge base", "user": user})


@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(request: Request):
    user = _staff_web_user(request)
    if user is None:
        return _staff_login_redirect()
    return templates.TemplateResponse(request, "notifications.html", {"title": "Notifications", "user": user})
