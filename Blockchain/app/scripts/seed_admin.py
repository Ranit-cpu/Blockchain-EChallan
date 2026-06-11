"""
Seed the initial admin user.
Usage: python scripts/seed_admin.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import AsyncSessionFactory
from app.database.redis import init_redis, close_redis
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def seed():
    configure_logging()
    await init_redis()

    async with AsyncSessionFactory() as session:
        service = UserService(session)
        await service.seed_roles()
        await session.commit()

        from app.repositories.user_repository import RoleRepository, UserRepository
        role_repo = RoleRepository(session)
        admin_role = await role_repo.get_by_name("admin")

        user_repo = UserRepository(session)
        existing = await user_repo.get_by_username("admin")
        if existing:
            logger.info("Admin user already exists")
        else:
            data = UserCreate(
                username="admin",
                email="admin@echallan.gov.in",
                password="Admin@1234",
                full_name="System Administrator",
                role_id=admin_role.id,
            )
            user = await service.create_user(data)
            await session.commit()
            logger.info("Admin user created", user_id=user.id)
            print(f"\n✅ Admin created: username=admin  password=Admin@1234\n")

    await close_redis()


if __name__ == "__main__":
    asyncio.run(seed())