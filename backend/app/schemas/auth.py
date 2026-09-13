from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str
    badge: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    badge: Optional[str] = None
    created_at: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
