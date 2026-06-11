from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditLog, session)

    async def get_filtered(
        self,
        user_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AuditLog], int]:
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if from_date:
            conditions.append(AuditLog.created_at >= from_date)
        if to_date:
            conditions.append(AuditLog.created_at <= to_date)

        base_stmt = select(AuditLog)
        count_stmt = select(func.count()).select_from(AuditLog)

        if conditions:
            base_stmt = base_stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = (await self.session.execute(count_stmt)).scalar_one()
        items = list(
            (
                await self.session.execute(
                    base_stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
                )
            ).scalars().all()
        )
        return items, total