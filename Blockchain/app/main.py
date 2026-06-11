from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.models import Base
from app.database.session import engine, close_db, AsyncSessionFactory
from app.core.logging import configure_logging, get_logger
from app.database.redis import init_redis, close_redis
from app.api.router import api_router
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.exception_handler import register_exception_handlers

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    configure_logging()

    logger.info(
        "Starting eChallan API",
        env=settings.APP_ENV,
        version="1.0.0"
    )

    # Initialize Redis
    await init_redis()

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")

    # Seed roles
    async with AsyncSessionFactory() as session:
        try:
            from app.services.user_service import UserService

            service = UserService(session)

            await service.seed_roles()
            await session.commit()

            logger.info("Default roles seeded")

        except Exception as e:
            logger.warning(
                "Role seeding failed",
                error=str(e)
            )

    logger.info("Application startup complete")

    yield

    logger.info("Shutting down eChallan API")

    await close_redis()
    await close_db()

    logger.info("Shutdown complete")


app = FastAPI(
    title="eChallan System API",
    description="Blockchain-based e-Challan management system with IPFS evidence storage",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_exceeded_handler
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_hosts_list, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=(
        settings.allowed_hosts_list + ["*"]
        if settings.APP_DEBUG
        else settings.allowed_hosts_list
    ),
)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/api/docs"
    }