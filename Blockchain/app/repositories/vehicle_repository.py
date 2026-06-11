from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vehicle import Vehicle, VehicleOwner
from app.repositories.base import BaseRepository


class VehicleOwnerRepository(BaseRepository[VehicleOwner]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(VehicleOwner, session)

    async def get_by_license_number(self, license_number: str) -> VehicleOwner | None:
        stmt = select(VehicleOwner).where(VehicleOwner.license_number == license_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> VehicleOwner | None:
        stmt = select(VehicleOwner).where(VehicleOwner.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> list[VehicleOwner]:
        stmt = (
            select(VehicleOwner)
            .where(
                VehicleOwner.full_name.ilike(f"%{query}%")
                | VehicleOwner.phone.ilike(f"%{query}%")
                | VehicleOwner.license_number.ilike(f"%{query}%")
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class VehicleRepository(BaseRepository[Vehicle]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Vehicle, session)

    async def get_by_registration(self, registration_number: str) -> Vehicle | None:
        stmt = (
            select(Vehicle)
            .options(selectinload(Vehicle.owner))
            .where(Vehicle.registration_number == registration_number)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_owner(self, vehicle_id: str) -> Vehicle | None:
        stmt = (
            select(Vehicle)
            .options(selectinload(Vehicle.owner))
            .where(Vehicle.id == vehicle_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: str) -> list[Vehicle]:
        stmt = (
            select(Vehicle)
            .options(selectinload(Vehicle.owner))
            .where(Vehicle.owner_id == owner_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_engine_number(self, engine_number: str) -> Vehicle | None:
        stmt = select(Vehicle).where(Vehicle.engine_number == engine_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_chassis_number(self, chassis_number: str) -> Vehicle | None:
        stmt = select(Vehicle).where(Vehicle.chassis_number == chassis_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_owner(self, offset: int = 0, limit: int = 20) -> list[Vehicle]:
        stmt = (
            select(Vehicle)
            .options(selectinload(Vehicle.owner))
            .offset(offset)
            .limit(limit)
            .order_by(Vehicle.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> list[Vehicle]:
        stmt = (
            select(Vehicle)
            .options(selectinload(Vehicle.owner))
            .where(
                Vehicle.registration_number.ilike(f"%{query}%")
                | Vehicle.make.ilike(f"%{query}%")
                | Vehicle.model.ilike(f"%{query}%")
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())