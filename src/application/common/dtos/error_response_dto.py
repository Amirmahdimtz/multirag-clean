from typing import Any, Optional

from pydantic import BaseModel


class ErrorResponseDto(BaseModel):
    success: bool = False
    message: str
    errors: Optional[Any] = None
