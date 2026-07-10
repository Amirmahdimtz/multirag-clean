from typing import Any, Optional

from src.core.exceptions.app_exception import AppException


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Unauthorized",
        errors: Optional[Any] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            errors=errors,
        )
