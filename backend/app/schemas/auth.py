from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.db.models import UserRole


class RegisterRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    mobile_number: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CITIZEN
    preferred_language: Literal['English', 'Marathi', 'Hindi'] = 'English'

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        cleaned = value.strip().replace(' ', '')
        if len(cleaned) < 8:
            raise ValueError('Mobile number must contain at least 8 digits.')
        if not cleaned.replace('+', '').replace('-', '').isdigit():
            raise ValueError('Mobile number must contain only digits, spaces, hyphens or a leading + sign.')
        return cleaned

    @model_validator(mode='after')
    def validate_password_match(self) -> 'RegisterRequest':
        if self.password != self.confirm_password:
            raise ValueError('Password and confirm_password must match.')
        return self


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: 'UserResponse'


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    mobile_number: str
    role: UserRole
    preferred_language: str
    is_active: bool
    is_verified: bool


TokenResponse.model_rebuild()
