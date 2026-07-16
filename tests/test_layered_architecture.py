"""Architecture contract: the app factory composes teaching layers, not a monolith."""


def test_teaching_layers_are_importable():
    from app.api.routes import auth, knowledge_base, system, tickets, users
    from app.core import database, dependencies, security
    from app.models import entities, enums
    from app.repositories import articles, tickets as ticket_repository, users as user_repository
    from app.schemas import articles as article_schemas, auth as auth_schemas, tickets as ticket_schemas
    from app.services import articles as article_services, auth as auth_services, tickets as ticket_services
    from app.web import routes

    assert all(
        [
            auth.router,
            knowledge_base.router,
            system.router,
            tickets.router,
            users.router,
            routes.router,
            database.Base,
            dependencies.require_roles,
            security.create_access_token,
            entities.User,
            enums.Role,
            user_repository.UserRepository,
            ticket_repository.TicketRepository,
            articles.ArticleRepository,
            auth_schemas.Login,
            ticket_schemas.TicketIn,
            article_schemas.ArticleIn,
            auth_services.AuthService,
            ticket_services.TicketService,
            article_services.ArticleService,
        ]
    )
