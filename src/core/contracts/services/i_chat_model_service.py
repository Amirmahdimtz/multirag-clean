from abc import ABC, abstractmethod
from typing import AsyncGenerator


class IChatModelService(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError
