from abc import ABC, abstractmethod

from fastapi import APIRouter


class BaseController(ABC):
    route_prefix: str = ""

    @abstractmethod
    def api(self) -> APIRouter:
        raise NotImplementedError
