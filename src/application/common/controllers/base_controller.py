from abc import ABC, abstractmethod
from typing import ClassVar

from fastapi import APIRouter


class BaseController(ABC):
    route_prefix: ClassVar[str] = ""

    @abstractmethod
    def api(self) -> APIRouter:
        raise NotImplementedError
