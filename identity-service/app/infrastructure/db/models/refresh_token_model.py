from sqlalchemy import Column, DateTime, BigInteger, String, ForeignKey, func
from app.infrastructure.db.base import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(
        BigInteger, ForeignKey("accounts.id"), nullable=False, index=True
    )
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
