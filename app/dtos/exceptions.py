from http import HTTPStatus
from typing import Any, Dict, Optional

class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or str(status_code)
        self.details = details or {}
        super().__init__(self.message)

class NotFoundException(AppException):
    def __init__(self, resource: str, **kwargs):
        super().__init__(
            message=f"{resource} not found",
            status_code=HTTPStatus.NOT_FOUND,
            **kwargs
        )

class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", **kwargs):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            **kwargs
        )

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            **kwargs
        )

class ForbiddenException(AppException):
    """Raised when user doesn't have permission"""
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            **kwargs
        )