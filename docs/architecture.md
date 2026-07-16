# HelpDesk EDU Architecture

```text
Browser / Mobile API Client
       |
FastAPI routes + JWT role dependencies
       |
Ticket, notification, and local-assistance services
       |
SQLAlchemy repositories and models
       |
SQLite default or PostgreSQL
```

## Layered MVC flow

Web routes render Jinja2 Bootstrap templates, while API controllers return Pydantic DTOs. The controller layer only receives HTTP input and delegates business rules to services. Services use repositories for persistence and preserve the existing ticket audit history.

### Persistent notifications

`Notification` is a SQLAlchemy model with `id`, `user_id`, optional `ticket_id`, `title`, `message`, `channel`, `type`, `read_at`, and `created_at`. `NotificationRepository` performs scoped queries; `NotificationService` creates in-app records and enforces ownership before marking a record read.

Ticket assignment creates a notification for the assignee. Comments notify the other ticket participant(s), and status changes or explicit closure notify requester and assignee except the actor. JWT-authenticated routes expose `GET /api/notifications`, `GET /api/notifications/unread-count`, and `POST /api/notifications/{id}/read`. The `/notifications` Jinja page and navigation link explain the authenticated unread workflow.

### Mobile integration

The `/api/mobile` router reuses `current_user` JWT dependency and `TicketService` rather than creating a separate ticket implementation:

- `GET /api/mobile/me`: compact signed-in user summary and open-ticket count.
- `GET /api/mobile/tickets`: compact tickets available to the current user (requesters get only their own tickets; staff retain normal ticket access).
- `GET /api/mobile/tickets/{id}`: compact detail with the same ownership/access rule.
- `POST /api/mobile/tickets`: mobile ticket creation through the standard ticket service and SLA/history flow.

### Safe local assistance

`AssistanceService` applies a fixed, deterministic keyword table for network, hardware, and software troubleshooting. `POST /api/assistance` is JWT-authenticated and returns only local hints plus a human-review disclaimer. It makes no external requests, requires no secret or model-provider configuration, and does not transmit ticket data outside the process. The ticket-detail template includes a local-assistance section that points users to the endpoint.
