from typing import Any, Optional

from src.core.exceptions.app_exception import AppException


class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
        errors: Optional[Any] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            errors=errors,
        )
