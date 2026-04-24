from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.api.dependencies import get_db
from app.api.v1.dependencies.auth_dependencies import get_current_account
from app.presentation.schemas.auth_request_schema import RegisterRequest, LoginRequest
from app.presentation.schemas.auth_response_schema import (
    MessageResponse,
    TokenResponse,
    AccountProfileResponse,
)
from app.infrastructure.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from app.application.use_cases.register_account import RegisterAccountUseCase
from app.application.use_cases.login_account import LoginAccountUseCase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"[ROUTE] Register called with email={request.email}")

    repository = SQLAlchemyAccountRepository(db)
    use_case = RegisterAccountUseCase(repository)

    try:
        result = use_case.execute(email=request.email, password=request.password)
        logger.info(f"[ROUTE] Register success for email={request.email}")
        return {"message": "Account registered successfully"}
    except ValueError as exc:
        logger.error(f"[ROUTE] Register failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"[ROUTE] Login called with email={request.email}")

    repository = SQLAlchemyAccountRepository(db)
    use_case = LoginAccountUseCase(repository)

    try:
        token = use_case.execute(email=request.email, password=request.password)
        logger.info(f"[ROUTE] Login success for email={request.email}")
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as exc:
        logger.error(f"[ROUTE] Login failed: {exc}")
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/me", response_model=AccountProfileResponse)
def get_me(current_account=Depends(get_current_account)):
    return {
        "id": current_account.id,
        "email": current_account.email,
        "role": current_account.role,
        "account_status": current_account.account_status,
        "is_email_verified": current_account.is_email_verified,
    }
