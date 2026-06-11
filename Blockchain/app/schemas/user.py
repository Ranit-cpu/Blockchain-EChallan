from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class RoleResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: str | None


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    badge_number: str | None = Field(default=None, max_length=50)
    role_id: int

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain alphanumeric characters, hyphens, underscores")
        return v.lower()


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    is_active: bool | None = None
    badge_number: str | None = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    username: str
    email: str
    full_name: str
    phone: str | None
    badge_number: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime
    role: RoleResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v