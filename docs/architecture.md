# HelpDesk EDU Architecture

```text
Browser / API Client
       |
FastAPI routes + JWT role dependencies
       |
Ticket helpers / audit service behavior
       |
SQLAlchemy 2 models and request-scoped Session
       |
SQLite default or PostgreSQL
```

Web routes render Jinja2 Bootstrap templates. API controllers return JSON DTO-shaped dictionaries. Every ticket mutation records a `History` audit event; comments and assignments remain linked to tickets and users.
