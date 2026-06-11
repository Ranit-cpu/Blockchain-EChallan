import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.repositories.audit_repository import AuditLogRepository
from app.core.enums import AuditAction
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AuditLogRepository(session)

    async def log(
        self,
        action: AuditAction,
        resource_type: str,
        user_id: str | None = None,
        resource_id: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        description: str | None = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
        )
        return await self.repo.create(log_entry)

    async def get_logs(
        self,
        user_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AuditLog], int]:
        return await self.repo.get_filtered(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            from_date=from_date,
            to_date=to_date,
            offset=offset,
            limit=limit,
        )