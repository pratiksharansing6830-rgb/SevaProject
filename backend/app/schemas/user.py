from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str = Field(..., min_length=2, max_length=120)
    email: str
    mobile_number: str
    role: UserRole
    preferred_language: str
    is_active: bool
    is_verified: bool
