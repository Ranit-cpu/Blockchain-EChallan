from fastapi import Depends, Request
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.services.session_service import SessionService
from app.core.exceptions import UnauthorizedError, ForbiddenError, SessionError
from app.core.enums import UserRole
from app.models.user import User
from app.config import settings

cookie_scheme = APIKeyCookie(name=settings.SESSION_COOKIE_NAME, auto_error=False)


async def get_current_user(
    request: Request,
    session_id: str | None = Depends(cookie_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    if not session_id:
        raise UnauthorizedError("Not authenticated")

    try:
        session_data = await SessionService.get_session(session_id)
    except SessionError:
        raise UnauthorizedError("Session expired or invalid")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_role(session_data["user_id"])

    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise ForbiddenError("Account deactivated")

    request.state.session_id = session_id
    request.state.current_user = user
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise ForbiddenError("Account is inactive")
    return user


def require_roles(*roles: UserRole):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role.name not in [r.value for r in roles]:
            raise ForbiddenError(
                f"Access denied. Required roles: {[r.value for r in roles]}"
            )
        return user
    return role_checker


def require_admin() -> User:
    return Depends(require_roles(UserRole.ADMIN))


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role.name != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")
    return user


async def get_officer_or_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.name not in (UserRole.ADMIN, UserRole.OFFICER):
        raise ForbiddenError("Officer or Admin access required")
    return user


async def get_any_authenticated(user: User = Depends(get_current_user)) -> User:
    return user