# HelpDesk EDU – Technical Support Management System

HelpDesk EDU is a complete, teachable semester-final project for a Spanish-speaking Programming II course. It evolves the weeks 1–8 in-memory help desk into a FastAPI application with a JSON API, a Bootstrap/Jinja2 web UI, persistence, authentication, roles, audit history, SLA indicators, and a knowledge base.

## Features and modules

- JWT authentication and the requester, technician, supervisor, and administrator roles.
- Users profile/listing, tickets, comments, assignment records, and audit history.
- Ticket status, cancellation, explicit close operation, filters, SLA due dates, and overdue reporting.
- Catalog values for categories, priorities, and statuses.
- Knowledge-base article CRUD and search.
- Dashboard summary by status, priority, category, overdue state, and technician workload.
- Server-rendered pages for login, dashboard, ticket list/detail/create, and knowledge-base browsing.

## Architecture and best practices

This repository intentionally shows a layered MVC adaptation for FastAPI rather than classic desktop MVC:

| Layer | Location | Responsibility |
|---|---|---|
| Model | `app/models/` | SQLAlchemy entities and domain enum values. |
| View | `app/web/templates/`, Pydantic response schemas, Swagger/OpenAPI | HTML for people and documented DTO responses for API consumers. |
| Controller | `app/api/routes/`, `app/web/routes.py` | HTTP input/output only; controllers delegate business work. |
| Service | `app/services/` | Ticket lifecycle, SLA, authorization-aware business rules, and history events. |
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

## Tests

```bash
uv run pytest -q
uv run python -c 'from app.main import app; print(app.title)'
docker compose config
```

Tests exercise health, JWT login, a role restriction, ticket create/list/detail flow, assignment/comment/status/history and explicit close flow, dashboard summary, and HTML responses for login, dashboard, and ticket-list pages.

## Example API flow

1. `POST /api/auth/login` with `{"email":"requester@example.com","password":"requester123"}`.
2. Send the returned token as `Authorization: Bearer <token>`.
3. `POST /api/tickets` with title, description, category, and priority.
4. A technician calls `PATCH /api/tickets/{id}/assign`, then `POST /api/tickets/{id}/comments` or `PATCH /api/tickets/{id}/status`.
5. Inspect `GET /api/tickets/{id}/history`, close with `POST /api/tickets/{id}/close`, and review `GET /api/dashboard`.

Low, Medium, High, and Critical tickets receive 72h, 48h, 24h, and 4h SLA targets respectively. Open tickets past their due date count as overdue.

## Student extension modules (intentionally not implemented)

- Notifications: email, in-app, or Observer-pattern delivery with delivery failure handling.
- Mobile integration: a mobile client consuming the documented API.
- AI-assisted suggestions: knowledge-base recommendations with explicit privacy, evaluation, and human-review safeguards.