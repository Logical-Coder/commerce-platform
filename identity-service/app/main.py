from fastapi import FastAPI
from app.core import logging  # just import to initialize
from app.core.config import settings
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine
from app.api.v1.routes.health_routes import router as health_router
from app.api.v1.routes.auth_routes import router as auth_router

app = FastAPI(title=settings.APP_NAME)

Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(auth_router)
