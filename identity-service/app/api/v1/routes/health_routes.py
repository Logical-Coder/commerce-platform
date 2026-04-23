from fastapi import APIRouter
from sqlalchemy import text
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.redis.redis_client import redis_client

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health():
    return {"status": "ok", "service": "identity-service"}


@router.get("/db")
def health_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "mysql"}
    finally:
        db.close()


@router.get("/redis")
def health_redis():
    pong = redis_client.ping()
    return {"status": "ok" if pong else "failed", "redis": "connected" if pong else "disconnected"}