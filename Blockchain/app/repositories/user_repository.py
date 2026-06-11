from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Role, session)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_id_with_role(self, user_id: str):
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_badge_number(self, badge_number: str) -> User | None:
        stmt = select(User).where(User.badge_number == badge_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_officers(self, offset: int = 0, limit: int = 20) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .join(User.role)
            .where(Role.name == "officer")
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_officers(self) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(User)
            .join(User.role)
            .where(Role.name == "officer")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_with_role(self, offset: int = 0, limit: int = 20) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .offset(offset)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts += 1
        await self.session.flush()

    async def reset_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts = 0
        await self.session.flush()