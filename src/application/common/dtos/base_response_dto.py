from typing import Any, Optional

from pydantic import BaseModel


class BaseResponseDto(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
