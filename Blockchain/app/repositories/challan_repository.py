from datetime import datetime
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.challan import (
    Challan, Violation, EvidenceFile, BlockchainTransaction, Payment
)
from app.models.vehicle import Vehicle
from app.repositories.base import BaseRepository
from app.core.enums import ChallanStatus, BlockchainTxStatus, PaymentStatus


class ViolationRepository(BaseRepository[Violation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Violation, session)

    async def get_by_code(self, code: str) -> Violation | None:
        stmt = select(Violation).where(Violation.code == code, Violation.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Violation]:
        stmt = select(Violation).where(Violation.is_active == True).order_by(Violation.code)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ChallanRepository(BaseRepository[Challan]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Challan, session)

    def _full_load(self):
        return (
            selectinload(Challan.vehicle).selectinload(Vehicle.owner),
            selectinload(Challan.violation),
            selectinload(Challan.officer),
            selectinload(Challan.evidence_files),
            selectinload(Challan.blockchain_transactions),
            selectinload(Challan.payments),
        )

    async def get_by_id_full(self, challan_id: str) -> Challan | None:
        stmt = (
            select(Challan)
            .options(*self._full_load())
            .where(Challan.id == challan_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_challan_number(self, challan_number: str) -> Challan | None:
        stmt = (
            select(Challan)
            .options(*self._full_load())
            .where(Challan.challan_number == challan_number)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash(self, challan_hash: str) -> Challan | None:
        stmt = (
            select(Challan)
            .options(*self._full_load())
            .where(Challan.challan_hash == challan_hash)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_duplicate(
        self, vehicle_id: str, violation_id: int, violation_datetime: str
    ) -> bool:
        """Detect duplicate: same vehicle, same violation within 1 hour window."""
        stmt = select(func.count()).select_from(Challan).where(
            and_(
                Challan.vehicle_id == vehicle_id,
                Challan.violation_id == violation_id,
                Challan.violation_datetime == violation_datetime,
                Challan.status != ChallanStatus.CANCELLED,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_filtered(
        self,
        status: str | None = None,
        vehicle_id: str | None = None,
        officer_id: str | None = None,
        violation_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Challan], int]:
        conditions = []
        if status:
            conditions.append(Challan.status == status)
        if vehicle_id:
            conditions.append(Challan.vehicle_id == vehicle_id)
        if officer_id:
            conditions.append(Challan.officer_id == officer_id)
        if violation_id:
            conditions.append(Challan.violation_id == violation_id)
        if from_date:
            conditions.append(Challan.created_at >= from_date)
        if to_date:
            conditions.append(Challan.created_at <= to_date)

        base_stmt = select(Challan).options(*self._full_load())
        count_stmt = select(func.count()).select_from(Challan)

        if conditions:
            base_stmt = base_stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        items_result = await self.session.execute(
            base_stmt.order_by(Challan.created_at.desc()).offset(offset).limit(limit)
        )
        items = list(items_result.scalars().all())
        return items, total

    async def get_by_vehicle(self, vehicle_id: str, offset: int = 0, limit: int = 20) -> list[Challan]:
        stmt = (
            select(Challan)
            .options(*self._full_load())
            .where(Challan.vehicle_id == vehicle_id)
            .order_by(Challan.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EvidenceFileRepository(BaseRepository[EvidenceFile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EvidenceFile, session)

    async def get_by_challan(self, challan_id: str) -> list[EvidenceFile]:
        stmt = select(EvidenceFile).where(EvidenceFile.challan_id == challan_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_cid(self, cid: str) -> EvidenceFile | None:
        stmt = select(EvidenceFile).where(EvidenceFile.ipfs_cid == cid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class BlockchainTxRepository(BaseRepository[BlockchainTransaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BlockchainTransaction, session)

    async def get_by_tx_hash(self, tx_hash: str) -> BlockchainTransaction | None:
        stmt = select(BlockchainTransaction).where(BlockchainTransaction.tx_hash == tx_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_confirmed_by_challan(self, challan_id: str) -> BlockchainTransaction | None:
        stmt = select(BlockchainTransaction).where(
            BlockchainTransaction.challan_id == challan_id,
            BlockchainTransaction.status == BlockchainTxStatus.CONFIRMED,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Payment, session)

    async def get_by_challan(self, challan_id: str) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.challan_id == challan_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_completed_by_challan(self, challan_id: str) -> Payment | None:
        stmt = select(Payment).where(
            Payment.challan_id == challan_id,
            Payment.status == PaymentStatus.COMPLETED,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Payment | None:
        stmt = select(Payment).where(Payment.transaction_reference == reference)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()