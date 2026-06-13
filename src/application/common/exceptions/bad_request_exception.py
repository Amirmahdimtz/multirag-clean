from typing import Any, Optional

from src.application.common.exceptions.app_exception import AppException


class BadRequestException(AppException):
    def __init__(
        self,
        message: str = "Bad request",
        errors: Optional[Any] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            errors=errors,
        )
