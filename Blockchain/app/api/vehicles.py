from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse,
    VehicleOwnerCreate, VehicleOwnerUpdate, VehicleOwnerResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, MessageResponse
from app.services.vehicle_service import VehicleService
from app.middleware.auth import get_current_user, get_admin_user, get_officer_or_admin
from app.models.user import User

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


# --- Owner endpoints ---
@router.post("/owners", response_model=APIResponse[VehicleOwnerResponse], status_code=201)
async def create_owner(
    data: VehicleOwnerCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[VehicleOwnerResponse]:
    service = VehicleService(db)
    owner = await service.create_owner(data, created_by_id=current_user.id)
    return APIResponse(message="Owner registered", data=VehicleOwnerResponse.model_validate(owner))


@router.get("/owners", response_model=PaginatedResponse[VehicleOwnerResponse])
async def list_owners(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_officer_or_admin),
) -> PaginatedResponse[VehicleOwnerResponse]:
    service = VehicleService(db)
    offset = (page - 1) * page_size
    owners, total = await service.list_owners(query=q, offset=offset, limit=page_size)
    return PaginatedResponse.create(
        items=[VehicleOwnerResponse.model_validate(o) for o in owners],
        total=total, page=page, page_size=page_size,
    )


@router.get("/owners/{owner_id}", response_model=APIResponse[VehicleOwnerResponse])
async def get_owner(
    owner_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_officer_or_admin),
) -> APIResponse[VehicleOwnerResponse]:
    service = VehicleService(db)
    owner = await service.get_owner(owner_id)
    return APIResponse(data=VehicleOwnerResponse.model_validate(owner))


@router.patch("/owners/{owner_id}", response_model=APIResponse[VehicleOwnerResponse])
async def update_owner(
    owner_id: str,
    data: VehicleOwnerUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[VehicleOwnerResponse]:
    service = VehicleService(db)
    owner = await service.update_owner(owner_id, data, updated_by_id=current_user.id)
    return APIResponse(message="Owner updated", data=VehicleOwnerResponse.model_validate(owner))


@router.get("/owners/{owner_id}/vehicles", response_model=APIResponse[list[VehicleResponse]])
async def get_owner_vehicles(
    owner_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[list[VehicleResponse]]:
    service = VehicleService(db)
    vehicles = await service.get_owner_vehicles(owner_id)
    return APIResponse(data=[VehicleResponse.model_validate(v) for v in vehicles])


# --- Vehicle endpoints ---
@router.post("", response_model=APIResponse[VehicleResponse], status_code=201)
async def register_vehicle(
    data: VehicleCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[VehicleResponse]:
    service = VehicleService(db)
    vehicle = await service.register_vehicle(data, created_by_id=current_user.id)
    vehicle_with_owner = await service.get_vehicle(vehicle.id)
    return APIResponse(message="Vehicle registered", data=VehicleResponse.model_validate(vehicle_with_owner))


@router.get("", response_model=PaginatedResponse[VehicleResponse])
async def list_vehicles(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_officer_or_admin),
) -> PaginatedResponse[VehicleResponse]:
    service = VehicleService(db)
    offset = (page - 1) * page_size
    vehicles, total = await service.list_vehicles(query=q, offset=offset, limit=page_size)
    return PaginatedResponse.create(
        items=[VehicleResponse.model_validate(v) for v in vehicles],
        total=total, page=page, page_size=page_size,
    )


@router.get("/registration/{reg_number}", response_model=APIResponse[VehicleResponse])
async def get_vehicle_by_registration(
    reg_number: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[VehicleResponse]:
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_registration(reg_number)
    return APIResponse(data=VehicleResponse.model_validate(vehicle))


@router.get("/{vehicle_id}", response_model=APIResponse[VehicleResponse])
async def get_vehicle(
    vehicle_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[VehicleResponse]:
    service = VehicleService(db)
    vehicle = await service.get_vehicle(vehicle_id)
    return APIResponse(data=VehicleResponse.model_validate(vehicle))


@router.patch("/{vehicle_id}", response_model=APIResponse[VehicleResponse])
async def update_vehicle(
    vehicle_id: str,
    data: VehicleUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[VehicleResponse]:
    service = VehicleService(db)
    vehicle = await service.update_vehicle(vehicle_id, data, updated_by_id=current_user.id)
    return APIResponse(message="Vehicle updated", data=VehicleResponse.model_validate(vehicle))