from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.user import LoginRequest, UserResponse
from app.schemas.common import APIResponse, MessageResponse
from app.services.user_service import UserService
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse[UserResponse])
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse[UserResponse]:
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    service = UserService(db)
    user, session_id = await service.authenticate(
        credentials.username, credentials.password, ip, user_agent
    )
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        max_age=settings.SESSION_TTL,
    )
    return APIResponse(
        message="Login successful",
        data=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    session_id = getattr(request.state, "session_id", None)
    if session_id:
        service = UserService(db)
        await service.logout(session_id, current_user.id)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)) -> APIResponse[UserResponse]:
    return APIResponse(data=UserResponse.model_validate(current_user))