from app.core.security import verify_password, create_access_token
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository


class LoginAccountUseCase:
    def __init__(self, repository: SQLAlchemyAccountRepository):
        self.repository = repository

    def execute(self, email: str, password: str):
        account = self.repository.get_by_email(email)
        if not account:
            raise ValueError("Invalid credentials")

        if not verify_password(password, account.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token(subject=account.email)
        return token