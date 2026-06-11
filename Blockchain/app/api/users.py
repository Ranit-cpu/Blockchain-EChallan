from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.user import UserCreate, UserUpdate, UserResponse, ChangePasswordRequest
from app.schemas.common import APIResponse, PaginatedResponse, MessageResponse
from app.services.user_service import UserService
from app.middleware.auth import get_current_user, get_admin_user, get_officer_or_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=APIResponse[UserResponse], status_code=201)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_admin_user),
) -> APIResponse[UserResponse]:
    service = UserService(db)
    user = await service.create_user(data, created_by_id=admin.id)
    try:
        return APIResponse(
            message="User created",
            data=UserResponse.model_validate(user)
        )
    except Exception as e:
        print(e)
        raise


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_admin_user),
) -> PaginatedResponse[UserResponse]:
    service = UserService(db)
    offset = (page - 1) * page_size
    users, total = await service.list_users(offset=offset, limit=page_size)
    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total, page=page, page_size=page_size,
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    # Users can only view own profile unless admin
    if current_user.role.name != "admin" and current_user.id != user_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Cannot view other user's profile")
    service = UserService(db)
    user = await service.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.patch("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    if current_user.role.name != "admin" and current_user.id != user_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Cannot update other user's profile")
    service = UserService(db)
    user = await service.update_user(user_id, data, updated_by_id=current_user.id)
    return APIResponse(message="User updated", data=UserResponse.model_validate(user))


@router.post("/{user_id}/change-password", response_model=MessageResponse)
async def change_password(
    user_id: str,
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    if current_user.id != user_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Cannot change another user's password")
    service = UserService(db)
    await service.change_password(user_id, data.current_password, data.new_password)
    return MessageResponse(message="Password changed. Please login again.")


@router.delete("/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_admin_user),
) -> MessageResponse:
    service = UserService(db)
    await service.deactivate_user(user_id, admin_id=admin.id)
    return MessageResponse(message="User deactivated")