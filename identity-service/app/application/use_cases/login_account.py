from app.core.security import verify_password, create_access_token
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository
import logging
logger = logging.getLogger(__name__)

class LoginAccountUseCase:
    def __init__(self, repository: SQLAlchemyAccountRepository):
        self.repository = repository
    def execute(self, email: str, password: str):
        logger.info(f"[USECASE] Login started for {email}")

        account = self.repository.get_by_email(email)

        if not account:
            logger.warning(f"[USECASE] Account not found: {email}")
            raise ValueError("Invalid credentials")

        logger.info(f"[USECASE] Account found, verifying password")

        if not verify_password(password, account.password_hash):
            logger.warning(f"[USECASE] Password mismatch for {email}")
            raise ValueError("Invalid credentials")

        logger.info(f"[USECASE] Password verified, creating token")

        token = create_access_token(subject=account.email)

        logger.info(f"[USECASE] Token created successfully for {email}")
        return token