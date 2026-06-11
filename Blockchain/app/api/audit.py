from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.audit import AuditLogResponse, AuditFilterParams
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService
from app.middleware.auth import get_admin_user
from app.core.enums import AuditAction
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    user_id: str | None = Query(default=None),
    action: AuditAction | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_admin_user),
) -> PaginatedResponse[AuditLogResponse]:
    service = AuditService(db)
    offset = (page - 1) * page_size
    logs, total = await service.get_logs(
        user_id=user_id,
        action=action.value if action else None,
        resource_type=resource_type,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=page_size,
    )
    return PaginatedResponse.create(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total, page=page, page_size=page_size,
    )