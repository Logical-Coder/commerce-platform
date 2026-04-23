from app.core.security import hash_password
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository


class RegisterAccountUseCase:
    def __init__(self, repository: SQLAlchemyAccountRepository):
        self.repository = repository

    def execute(self, email: str, password: str):
        existing_account = self.repository.get_by_email(email)
        if existing_account:
            raise ValueError("Email already registered")

        password_hash = hash_password(password)
        return self.repository.create(email=email, password_hash=password_hash)