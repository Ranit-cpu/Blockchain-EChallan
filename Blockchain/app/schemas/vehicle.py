from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from app.core.enums import VehicleType


class VehicleOwnerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str = Field(min_length=10, max_length=20)
    address: str = Field(min_length=5, max_length=1000)
    license_number: str = Field(min_length=5, max_length=50)
    license_expiry: str | None = None
    id_proof_type: str | None = Field(default=None, max_length=50)
    id_proof_number: str | None = Field(default=None, max_length=100)
    user_id: str | None = None


class VehicleOwnerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    address: str | None = Field(default=None, min_length=5, max_length=1000)
    license_expiry: str | None = None
    is_active: bool | None = None


class VehicleOwnerResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    full_name: str
    email: str | None
    phone: str
    address: str
    license_number: str
    license_expiry: str | None
    is_active: bool
    created_at: datetime


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=5, max_length=20)
    owner_id: str
    vehicle_type: VehicleType
    make: str = Field(min_length=2, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1900, le=2030)
    color: str = Field(min_length=2, max_length=50)
    engine_number: str = Field(min_length=5, max_length=100)
    chassis_number: str = Field(min_length=5, max_length=100)
    fuel_type: str = Field(min_length=2, max_length=30)
    insurance_valid_till: str | None = None
    puc_valid_till: str | None = None

    @field_validator("registration_number")
    @classmethod
    def validate_registration(cls, v: str) -> str:
        pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
        clean = v.upper().replace(" ", "")
        if not re.match(pattern, clean):
            raise ValueError("Invalid vehicle registration number format (e.g. MH12AB1234)")
        return clean


class VehicleUpdate(BaseModel):
    color: str | None = Field(default=None, min_length=2, max_length=50)
    insurance_valid_till: str | None = None
    puc_valid_till: str | None = None
    is_active: bool | None = None
    owner_id: str | None = None


class VehicleResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    registration_number: str
    vehicle_type: str
    make: str
    model: str
    year: int
    color: str
    fuel_type: str
    insurance_valid_till: str | None
    puc_valid_till: str | None
    is_active: bool
    created_at: datetime
    owner: VehicleOwnerResponse