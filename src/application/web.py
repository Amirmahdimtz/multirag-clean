from fastapi import FastAPI
import uvicorn

from src.application.health.health_controller import HealthController
from src.infrastructure.config.config_reader import ConfigReader


class WebService:
    def __init__(self, config_reader: ConfigReader) -> None:
        self.config_reader = config_reader
        self.app = FastAPI(
            title=self.config_reader.get("application.name", "MultiRAG Clean"),
            version=self.config_reader.get("application.version", "0.1.0"),
        )

        self.__register_controllers()

    def __register_controllers(self) -> None:
        api_prefix = self.config_reader.get(
            "application.api_prefix", "/api/v1")

        health_controller = HealthController(
            config_reader=self.config_reader,
        )

        self.app.include_router(
            health_controller.api(),
            prefix=f"{api_prefix}/health",
        )

    def start(self) -> None:
        host = self.config_reader.get("application.host", "127.0.0.1")
        port = int(self.config_reader.get("application.port", 8000))

        uvicorn.run(
            self.app,
            host=host,
            port=port,
        )
