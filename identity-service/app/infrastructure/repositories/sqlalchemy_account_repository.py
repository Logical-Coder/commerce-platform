from sqlalchemy.orm import Session
from app.infrastructure.db.models.account_model import AccountModel


import logging

logger = logging.getLogger(__name__)


class SQLAlchemyAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        logger.info(f"[REPO] Fetching account by email={email}")
        return self.db.query(AccountModel).filter(AccountModel.email == email).first()

    def get_by_id(self, account_id: int):
        return self.db.query(AccountModel).filter(AccountModel.id == account_id).first()

    def create(self, email: str, password_hash: str, role: str = "CUSTOMER"):
        logger.info(f"[REPO] Creating account for email={email}")

        account = AccountModel(
            email=email,
            password_hash=password_hash,
            role=role,
            account_status="ACTIVE",
            is_email_verified=False,
        )

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        logger.info(f"[REPO] Account stored with id={account.id}")

        return account
