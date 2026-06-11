from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vehicle import Vehicle, VehicleOwner
from app.repositories.vehicle_repository import VehicleRepository, VehicleOwnerRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOwnerCreate, VehicleOwnerUpdate
from app.core.exceptions import NotFoundError, ConflictError
from app.core.enums import AuditAction
from app.services.audit_service import AuditService
from app.core.logging import get_logger

logger = get_logger(__name__)


class VehicleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.vehicle_repo = VehicleRepository(session)
        self.owner_repo = VehicleOwnerRepository(session)
        self.audit = AuditService(session)

    async def create_owner(self, data: VehicleOwnerCreate, created_by_id: str) -> VehicleOwner:
        existing = await self.owner_repo.get_by_license_number(data.license_number)
        if existing:
            raise ConflictError(f"Owner with license '{data.license_number}' already registered")

        owner = VehicleOwner(**data.model_dump())
        created = await self.owner_repo.create(owner)
        await self.audit.log(
            action=AuditAction.CREATE,
            resource_type="vehicle_owner",
            user_id=created_by_id,
            resource_id=created.id,
            description=f"Owner {data.full_name} registered",
        )
        return created

    async def get_owner(self, owner_id: str) -> VehicleOwner:
        owner = await self.owner_repo.get_by_id(owner_id)
        if not owner:
            raise NotFoundError(f"Owner {owner_id} not found")
        return owner

    async def update_owner(
        self, owner_id: str, data: VehicleOwnerUpdate, updated_by_id: str
    ) -> VehicleOwner:
        owner = await self.owner_repo.get_by_id(owner_id)
        if not owner:
            raise NotFoundError(f"Owner {owner_id} not found")

        old = {"full_name": owner.full_name, "phone": owner.phone}
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(owner, field, value)

        updated = await self.owner_repo.update(owner)
        await self.audit.log(
            action=AuditAction.UPDATE,
            resource_type="vehicle_owner",
            user_id=updated_by_id,
            resource_id=owner_id,
            old_values=old,
            description=f"Owner {owner.full_name} updated",
        )
        return updated

    async def list_owners(
        self, query: str | None = None, offset: int = 0, limit: int = 20
    ) -> tuple[list[VehicleOwner], int]:
        if query:
            items = await self.owner_repo.search(query, offset=offset, limit=limit)
            return items, len(items)
        items = await self.owner_repo.get_all(offset=offset, limit=limit)
        total = await self.owner_repo.count_all()
        return items, total

    async def register_vehicle(self, data: VehicleCreate, created_by_id: str) -> Vehicle:
        if await self.vehicle_repo.get_by_registration(data.registration_number):
            raise ConflictError(f"Vehicle '{data.registration_number}' already registered")
        if await self.vehicle_repo.get_by_engine_number(data.engine_number):
            raise ConflictError("Engine number already registered")
        if await self.vehicle_repo.get_by_chassis_number(data.chassis_number):
            raise ConflictError("Chassis number already registered")

        owner = await self.owner_repo.get_by_id(data.owner_id)
        if not owner:
            raise NotFoundError(f"Owner {data.owner_id} not found")

        vehicle = Vehicle(**data.model_dump())
        created = await self.vehicle_repo.create(vehicle)
        await self.audit.log(
            action=AuditAction.CREATE,
            resource_type="vehicle",
            user_id=created_by_id,
            resource_id=created.id,
            description=f"Vehicle {data.registration_number} registered",
        )
        return created

    async def get_vehicle(self, vehicle_id: str) -> Vehicle:
        vehicle = await self.vehicle_repo.get_by_id_with_owner(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        return vehicle

    async def get_vehicle_by_registration(self, reg: str) -> Vehicle:
        vehicle = await self.vehicle_repo.get_by_registration(reg.upper().replace(" ", ""))
        if not vehicle:
            raise NotFoundError(f"Vehicle {reg} not found")
        return vehicle

    async def update_vehicle(
        self, vehicle_id: str, data: VehicleUpdate, updated_by_id: str
    ) -> Vehicle:
        vehicle = await self.vehicle_repo.get_by_id_with_owner(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")

        if data.owner_id:
            owner = await self.owner_repo.get_by_id(data.owner_id)
            if not owner:
                raise NotFoundError(f"Owner {data.owner_id} not found")

        old = {"color": vehicle.color, "insurance_valid_till": vehicle.insurance_valid_till}
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(vehicle, field, value)

        updated = await self.vehicle_repo.update(vehicle)
        await self.audit.log(
            action=AuditAction.UPDATE,
            resource_type="vehicle",
            user_id=updated_by_id,
            resource_id=vehicle_id,
            old_values=old,
            description=f"Vehicle {vehicle.registration_number} updated",
        )
        return updated

    async def list_vehicles(
        self, query: str | None = None, offset: int = 0, limit: int = 20
    ) -> tuple[list[Vehicle], int]:
        if query:
            items = await self.vehicle_repo.search(query, offset=offset, limit=limit)
            return items, len(items)
        items = await self.vehicle_repo.list_with_owner(offset=offset, limit=limit)
        total = await self.vehicle_repo.count_all()
        return items, total

    async def get_owner_vehicles(self, owner_id: str) -> list[Vehicle]:
        owner = await self.owner_repo.get_by_id(owner_id)
        if not owner:
            raise NotFoundError(f"Owner {owner_id} not found")
        return await self.vehicle_repo.get_by_owner(owner_id)