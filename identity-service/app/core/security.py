from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
import bcrypt
from app.core.config import settings

import logging
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    logger.info("[SECURITY] Hashing password")
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.info("[SECURITY] Verifying password")
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(subject: str) -> str:
    logger.info(f"[SECURITY] Creating JWT token for {subject}")
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    logger.info("[SECURITY] Decoding token")
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc