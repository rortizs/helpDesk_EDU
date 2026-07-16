# HelpDesk EDU – Technical Support Management System

HelpDesk EDU is a complete, teachable semester-final project for a Spanish-speaking Programming II course. It evolves the weeks 1–8 in-memory help desk into a FastAPI application with a JSON API, a Bootstrap/Jinja2 web UI, persistence, authentication, roles, audit history, SLA indicators, a knowledge base, and three demonstrative extension modules.

## Features and modules

- JWT authentication and the requester, technician, supervisor, and administrator roles.
- Users profile/listing, tickets, comments, assignment records, and audit history.
- Ticket status, cancellation, explicit close operation, filters, SLA due dates, and overdue reporting.
- Catalog values for categories, priorities, and statuses.
- Knowledge-base article CRUD and search.
- Dashboard summary by status, priority, category, overdue state, and technician workload.
- Server-rendered pages for login, dashboard, ticket list/detail/create, knowledge-base browsing, and notifications.
- Persistent in-app notifications for assignments, comments, status changes, and ticket closure.
- JWT-protected compact mobile endpoints under `/api/mobile`.
- Deterministic local troubleshooting assistance with no external AI/provider calls.

## Architecture and best practices

This repository intentionally shows a layered MVC adaptation for FastAPI rather than classic desktop MVC:

| Layer | Location | Responsibility |
|---|---|---|
| Model | `app/models/` | SQLAlchemy entities and domain enum values. |
| View | `app/web/templates/`, Pydantic response schemas, Swagger/OpenAPI | HTML for people and documented DTO responses for API consumers. |
| Controller | `app/api/routes/`, `app/web/routes.py` | HTTP input/output only; controllers delegate business work. |
| Service | `app/services/` | Ticket lifecycle, notifications, local assistance, SLA, and authorization-aware business rules. |
| Repository | `app/repositories/` | SQLAlchemy query and persistence operations. |
| Infrastructure | `app/core/` | Settings, security, dependencies, and request-scoped database session lifecycle. |

FastAPI does not impose a desktop-style MVC framework. Layered MVC is useful here because models remain ORM/domain objects, route handlers act as controllers, templates and API schemas are views, and services/repositories prevent controllers from becoming the place where every business rule and database query lives. Dependencies provide reusable JWT and role checks; Pydantic DTOs keep external request/response contracts separate from database entities.

## Local setup (SQLite)

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv venv .venv --python 3.12
uv sync --all-groups
cp .env.example .env
uv run uvicorn app.main:app --reload
```

The default `DATABASE_URL=sqlite:///./helpdesk.db` creates the classroom SQLite database and deterministic demo users on startup. Browse the web UI at `http://127.0.0.1:8000/login`, Swagger UI at `http://127.0.0.1:8000/docs`, and OpenAPI JSON at `http://127.0.0.1:8000/openapi.json`.

## Environment variables

| Variable | Purpose | Default/example |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy URL; SQLite locally or PostgreSQL in Docker | `sqlite:///./helpdesk.db` |
| `JWT_SECRET` | JWT signing secret | Set a strong unique value outside development. |
| `JWT_EXPIRE_HOURS` | Token lifetime in hours | `8` |

Never commit `.env` files or production secrets. `.env.example` is safe to commit because it contains placeholders only.

## Docker Compose with PostgreSQL

```bash
export JWT_SECRET='replace-this-for-any-shared-environment'
docker compose up --build
```

Compose starts the FastAPI application on `http://localhost:8000` and PostgreSQL 16. The application receives a PostgreSQL `DATABASE_URL` and creates/seed tables at startup for this classroom demonstration.

## Demo users

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@example.com` | `admin123` |
| Supervisor | `supervisor@example.com` | `supervisor123` |
| Technician | `technician@example.com` | `technician123` |
| Requester | `requester@example.com` | `requester123` |

These credentials are educational seed data only. Replace them and rotate `JWT_SECRET` before any real deployment.

## Demonstrative extension modules

### Notifications

All notification routes require `Authorization: Bearer <token>`:

- `GET /api/notifications` returns only the current user's records and an `unread_count`.
- `GET /api/notifications/unread-count` returns the compact badge value.
- `POST /api/notifications/{id}/read` marks an owned notification read; another user's ID is not accessible.

Ticket assignment notifies the assignee. Comments notify other requester/assignee participants; status changes and explicit closure notify non-actor participants. Visit `/notifications` for the Jinja notification section; its API-first design keeps JWT ownership enforcement in the controller/service flow.

### Mobile API

The API-ready mobile surface is compact and preserves the same JWT and ticket access rules as the primary API:

- `GET /api/mobile/me`
- `GET /api/mobile/tickets`
- `GET /api/mobile/tickets/{ticket_id}`
- `POST /api/mobile/tickets`

Requesters see only their own tickets. Staff retain normal ticket access. Mobile creates use the same `TicketService`, so SLA due dates and audit history behave identically to web/API ticket creation.

### Local assistance safety

`POST /api/assistance` accepts a ticket-like `{title, description, category}` payload and returns deterministic network, hardware, or software hints when known keywords match. It has no external model call, no provider credentials, no network transmission, and returns an explicit human-review disclaimer. The ticket detail page includes a **Local assistance suggestions** section. Hints are educational troubleshooting prompts, not automated actions or authoritative diagnoses.

## Tests

```bash
uv run pytest -q
uv run python -c 'from app.main import app; print(app.title)'
docker compose config
```

Tests exercise health, JWT login, role restrictions, ticket lifecycle/history, persistent notification ownership and unread state, authenticated mobile summary/list behavior, deterministic local assistance matching, and key Jinja pages.

## Example API flow

1. `POST /api/auth/login` with `{"email":"requester@example.com","password":"requester123"}`.
2. Send the returned token as `Authorization: Bearer <token>`.
3. `POST /api/tickets` with title, description, category, and priority.
4. A technician calls `PATCH /api/tickets/{id}/assign`, then `POST /api/tickets/{id}/comments` or `PATCH /api/tickets/{id}/status`.
5. Inspect `GET /api/notifications`, `GET /api/tickets/{id}/history`, close with `POST /api/tickets/{id}/close`, and review `GET /api/dashboard`.
6. A mobile client can call `/api/mobile/me` and `/api/mobile/tickets` with the same token; an authenticated client can request a local hint from `/api/assistance`.

Low, Medium, High, and Critical tickets receive 72h, 48h, 24h, and 4h SLA targets respectively. Open tickets past their due date count as overdue.
