import json
from datetime import datetime, timezone
from app.config import settings
from app.core.exceptions import SessionError
from app.core.security import generate_session_id
from app.database.redis import get_session_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

SESSION_PREFIX = "session"


class SessionService:
    @staticmethod
    def _key(session_id: str) -> str:
        return f"{SESSION_PREFIX}:{session_id}"

    @staticmethod
    async def create_session(user_id: str, role: str, ip_address: str, user_agent: str) -> str:
        session_id = generate_session_id()
        redis = get_session_redis()
        session_data = {
            "user_id": user_id,
            "role": role,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
        await redis.set(
            SessionService._key(session_id),
            json.dumps(session_data),
            ex=settings.SESSION_TTL,
        )
        logger.info("Session created", user_id=user_id, role=role)
        return session_id

    @staticmethod
    async def get_session(session_id: str) -> dict:
        redis = get_session_redis()
        data = await redis.get(SessionService._key(session_id))
        if not data:
            raise SessionError("Session not found or expired")
        session = json.loads(data)
        # Refresh TTL on activity
        await redis.expire(SessionService._key(session_id), settings.SESSION_TTL)
        # Update last activity
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        await redis.set(
            SessionService._key(session_id), json.dumps(session), ex=settings.SESSION_TTL
        )
        return session

    @staticmethod
    async def destroy_session(session_id: str) -> None:
        redis = get_session_redis()
        await redis.delete(SessionService._key(session_id))
        logger.info("Session destroyed", session_id=session_id[:8])

    @staticmethod
    async def invalidate_user_sessions(user_id: str) -> int:
        """Invalidate all sessions for a user (admin action)."""
        redis = get_session_redis()
        pattern = f"{SESSION_PREFIX}:*"
        count = 0
        async for key in redis.scan_iter(pattern):
            data = await redis.get(key)
            if data:
                session = json.loads(data)
                if session.get("user_id") == user_id:
                    await redis.delete(key)
                    count += 1
        logger.info("User sessions invalidated", user_id=user_id, count=count)
        return count

    @staticmethod
    async def session_exists(session_id: str) -> bool:
        redis = get_session_redis()
        return bool(await redis.exists(SessionService._key(session_id)))