from abc import ABC, abstractmethod


class BaseChatModelService(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError
