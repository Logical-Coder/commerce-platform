from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import decode_access_token
from app.infrastructure.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)

security_scheme = HTTPBearer()

import logging

logger = logging.getLogger(__name__)


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    logger.info("[AUTH] Extracting token")

    token = credentials.credentials

    logger.info("[AUTH] Decoding token")

    payload = decode_access_token(token)

    email = payload.get("sub")
    logger.info(f"[AUTH] Token belongs to {email}")

    repository = SQLAlchemyAccountRepository(db)
    account = repository.get_by_email(email)

    if not account:
        logger.error("[AUTH] Account not found")
        raise HTTPException(...)

    logger.info(f"[AUTH] Authenticated user id={account.id}")
    return account
