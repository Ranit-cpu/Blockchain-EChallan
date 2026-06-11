from datetime import datetime
from pydantic import BaseModel
from app.core.enums import AuditAction


class AuditLogResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    description: str | None
    ip_address: str | None
    created_at: datetime


class AuditFilterParams(BaseModel):
    user_id: str | None = None
    action: AuditAction | None = None
    resource_type: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size