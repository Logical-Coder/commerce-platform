from app.core.security import hash_password
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository

import logging
logger = logging.getLogger(__name__)

class RegisterAccountUseCase:
    def __init__(self, repository: SQLAlchemyAccountRepository):
        self.repository = repository

    def execute(self, email: str, password: str):
        logger.info(f"[USECASE] Register started for {email}")

        existing_account = self.repository.get_by_email(email)

        if existing_account:
            logger.warning(f"[USECASE] Email already exists: {email}")
            raise ValueError("Email already registered")

        logger.info(f"[USECASE] Hashing password")

        password_hash = hash_password(password)

        logger.info(f"[USECASE] Creating account in DB")

        account = self.repository.create(email=email, password_hash=password_hash)

        logger.info(f"[USECASE] Account created with id={account.id}")

        return account
