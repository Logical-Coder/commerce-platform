from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountProfileResponse(BaseModel):
    id: int
    email: str
    role: str
    account_status: str
    is_email_verified: bool
