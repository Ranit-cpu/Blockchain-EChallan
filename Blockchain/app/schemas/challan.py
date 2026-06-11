from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from app.core.enums import ChallanStatus, PaymentMethod, PaymentStatus, BlockchainTxStatus


class ViolationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    fine_amount: Decimal = Field(gt=0, decimal_places=2)
    points_deducted: int = Field(default=0, ge=0)


class ViolationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    fine_amount: Decimal = Field(..., decimal_places=2)
    points_deducted: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ViolationResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    code: str
    name: str
    description: str | None
    fine_amount: Decimal
    points_deducted: int
    is_active: bool


class ChallanCreate(BaseModel):
    vehicle_registration: str = Field(min_length=5, max_length=20)
    violation_code: str = Field(min_length=2, max_length=20)
    location: str = Field(min_length=5, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    violation_datetime: str
    notes: str | None = None
    due_date: str | None = None

    @field_validator("vehicle_registration")
    @classmethod
    def normalize_registration(cls, v: str) -> str:
        return v.upper().replace(" ", "")


class ChallanUpdate(BaseModel):
    status: ChallanStatus | None = None
    notes: str | None = None
    due_date: str | None = None
    is_disputed: bool | None = None
    dispute_reason: str | None = None


class EvidenceFileResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    ipfs_cid: str
    file_name: str
    file_type: str
    file_size: int
    ipfs_url: str
    description: str | None
    created_at: datetime


class BlockchainTxResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    tx_hash: str
    block_number: int | None
    contract_address: str
    status: str
    gas_used: int | None
    confirmed_at: str | None
    created_at: datetime


class PaymentCreate(BaseModel):
    challan_id: str
    payment_method: PaymentMethod
    transaction_reference: str | None = Field(default=None, max_length=255)
    payment_gateway: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class PaymentResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    challan_id: str
    amount: Decimal
    payment_method: str
    status: str
    transaction_reference: str | None
    payment_gateway: str | None
    paid_at: str | None
    created_at: datetime


class ChallanResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    challan_number: str
    challan_hash: str
    status: str
    fine_amount: Decimal
    location: str
    latitude: float | None
    longitude: float | None
    violation_datetime: str
    notes: str | None
    due_date: str | None
    is_disputed: bool
    dispute_reason: str | None
    created_at: datetime
    vehicle: "VehicleBasic"
    violation: ViolationResponse
    officer: "OfficerBasic"
    evidence_files: list[EvidenceFileResponse] = []
    blockchain_transactions: list[BlockchainTxResponse] = []
    payments: list[PaymentResponse] = []


class VehicleBasic(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    registration_number: str
    make: str
    model: str
    year: int
    color: str


class OfficerBasic(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    full_name: str
    badge_number: str | None


class ChallanVerifyResponse(BaseModel):
    is_valid: bool
    challan_number: str
    challan_hash: str
    blockchain_verified: bool
    tx_hash: str | None
    message: str


class ChallanFilterParams(BaseModel):
    status: ChallanStatus | None = None
    vehicle_registration: str | None = None
    officer_id: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    violation_code: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size