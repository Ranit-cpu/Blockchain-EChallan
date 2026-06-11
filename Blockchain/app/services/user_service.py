from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Role
from app.repositories.user_repository import UserRepository, RoleRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password, generate_session_id
from app.core.exceptions import (
    NotFoundError, ConflictError, UnauthorizedError, ForbiddenError
)
from app.core.enums import AuditAction
from app.services.session_service import SessionService
from app.services.audit_service import AuditService
from app.core.logging import get_logger

logger = get_logger(__name__)

MAX_FAILED_ATTEMPTS = 5


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.audit = AuditService(session)

    async def create_user(
        self, data: UserCreate, created_by_id: str | None = None
    ) -> User:
        if await self.user_repo.get_by_username(data.username):
            raise ConflictError(f"Username '{data.username}' already taken")
        if await self.user_repo.get_by_email(data.email):
            raise ConflictError(f"Email '{data.email}' already registered")
        if data.badge_number and await self.user_repo.get_by_badge_number(data.badge_number):
            raise ConflictError(f"Badge number '{data.badge_number}' already exists")

        role = await self.role_repo.get_by_id(data.role_id)
        if not role:
            raise NotFoundError(f"Role with id {data.role_id} not found")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            badge_number=data.badge_number,
            role_id=data.role_id,
            is_verified=True,
        )
        created = await self.user_repo.create(user)
        created = await self.user_repo.get_by_id_with_role(created.id)
        await self.audit.log(
            action=AuditAction.CREATE,
            resource_type="user",
            user_id=created_by_id,
            resource_id=created.id,
            description=f"User {data.username} created",
        )
        logger.info("User created", user_id=created.id, username=data.username)
        return created

    async def authenticate(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> tuple[User, str]:
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise ForbiddenError("Account is deactivated")

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            raise ForbiddenError("Account locked due to too many failed attempts")

        if not verify_password(password, user.hashed_password):
            await self.user_repo.increment_failed_attempts(user)
            await self.audit.log(
                action=AuditAction.LOGIN,
                resource_type="user",
                user_id=user.id,
                ip_address=ip_address,
                description=f"Failed login attempt for {username}",
            )
            raise UnauthorizedError("Invalid credentials")

        await self.user_repo.reset_failed_attempts(user)
        user.last_login_at = datetime.now(timezone.utc).isoformat()
        await self.user_repo.update(user)

        session_id = await SessionService.create_session(
            user_id=user.id,
            role=user.role.name,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.audit.log(
            action=AuditAction.LOGIN,
            resource_type="user",
            user_id=user.id,
            ip_address=ip_address,
            description=f"Successful login for {username}",
        )
        return user, session_id

    async def logout(self, session_id: str, user_id: str) -> None:
        await SessionService.destroy_session(session_id)
        await self.audit.log(
            action=AuditAction.LOGOUT,
            resource_type="user",
            user_id=user_id,
            description="User logged out",
        )

    async def get_user(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id_with_role(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def update_user(
        self, user_id: str, data: UserUpdate, updated_by_id: str
    ) -> User:
        user = await self.user_repo.get_by_id_with_role(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        if data.email and data.email != user.email:
            if await self.user_repo.get_by_email(data.email):
                raise ConflictError(f"Email '{data.email}' already registered")

        old_values = {"full_name": user.full_name, "email": user.email, "phone": user.phone}
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)

        updated = await self.user_repo.update(user)
        await self.audit.log(
            action=AuditAction.UPDATE,
            resource_type="user",
            user_id=updated_by_id,
            resource_id=user_id,
            old_values=old_values,
            new_values=data.model_dump(exclude_none=True),
            description=f"User {user.username} updated",
        )
        return updated

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user = await self.user_repo.get_by_id_with_role(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")
        user.hashed_password = hash_password(new_password)
        await self.user_repo.update(user)
        await SessionService.invalidate_user_sessions(user_id)
        await self.audit.log(
            action=AuditAction.UPDATE,
            resource_type="user",
            user_id=user_id,
            resource_id=user_id,
            description="Password changed",
        )

    async def list_users(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        users = await self.user_repo.list_with_role(offset=offset, limit=limit)
        total = await self.user_repo.count_all()
        return users, total

    async def deactivate_user(self, user_id: str, admin_id: str) -> User:
        user = await self.user_repo.get_by_id_with_role(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.is_active = False
        updated = await self.user_repo.update(user)
        await SessionService.invalidate_user_sessions(user_id)
        await self.audit.log(
            action=AuditAction.UPDATE,
            resource_type="user",
            user_id=admin_id,
            resource_id=user_id,
            description=f"User {user.username} deactivated",
        )
        return updated

    async def seed_roles(self) -> None:
        roles = [
            ("admin", "System administrator with full access"),
            ("officer", "Traffic officer who can issue challans"),
            ("owner", "Vehicle owner who can view their challans"),
        ]
        for name, description in roles:
            existing = await self.role_repo.get_by_name(name)
            if not existing:
                role = Role(name=name, description=description)
                await self.role_repo.create(role)
                logger.info("Role seeded", role=name)