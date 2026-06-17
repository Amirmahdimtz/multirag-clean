from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponseDto(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
