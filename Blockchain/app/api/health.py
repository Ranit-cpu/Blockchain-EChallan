from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db_session
from app.database.redis import get_redis
from app.ipfs.client import get_ipfs_client
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db_session)) -> dict:
    checks: dict[str, str] = {}

    # DB
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"

    # Redis
    try:
        redis = get_redis()
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"

    # IPFS
    try:
        ipfs = get_ipfs_client()
        ipfs_ok = await ipfs.health_check()
        checks["ipfs"] = "healthy" if ipfs_ok else "unhealthy"
    except Exception as e:
        checks["ipfs"] = f"unhealthy: {e}"

    overall = "healthy" if all("healthy" == v for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}