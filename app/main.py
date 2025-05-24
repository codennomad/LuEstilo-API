from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from lixo.routes import router as auth_router

from sentry_sdk import init as sentry_init

from app.routers import auth

if settings.SENTRY_DSN and "exemplo" not in settings.SENTRY_DSN:
    sentry_init(dsn=settings.SENTRY_DSN)

def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION
    )
    app.include_router(auth_router)
    app.include_router(auth.router)

    # Aqui futuramente: routers, middlewares, eventos
    
    return app

app = create_app()
