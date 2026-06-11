from typing import Any


class AppBaseException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppBaseException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class UnauthorizedError(AppBaseException):
    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Authentication required"


class ForbiddenError(AppBaseException):
    status_code = 403
    error_code = "FORBIDDEN"
    message = "Insufficient permissions"


class ConflictError(AppBaseException):
    status_code = 409
    error_code = "CONFLICT"
    message = "Resource already exists"


class ValidationError(AppBaseException):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class DuplicateViolationError(AppBaseException):
    status_code = 409
    error_code = "DUPLICATE_VIOLATION"
    message = "Duplicate violation detected"


class BlockchainError(AppBaseException):
    status_code = 503
    error_code = "BLOCKCHAIN_ERROR"
    message = "Blockchain operation failed"


class IPFSError(AppBaseException):
    status_code = 503
    error_code = "IPFS_ERROR"
    message = "IPFS operation failed"


class PaymentError(AppBaseException):
    status_code = 400
    error_code = "PAYMENT_ERROR"
    message = "Payment processing failed"


class SessionError(AppBaseException):
    status_code = 401
    error_code = "SESSION_ERROR"
    message = "Session invalid or expired"


class RateLimitError(AppBaseException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Rate limit exceeded"