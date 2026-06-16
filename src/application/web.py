from typing import Sequence

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.application.common.controllers.base_controller import BaseController
from src.application.common.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.application.common.exceptions.app_exception import AppException
from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.infrastructure_collection import InfrastructureCollection


class WebService:
    def __init__(
        self,
        config_reader: ConfigReader,
        controllers: Sequence[BaseController],
    ) -> None:
        self.config_reader = config_reader
        self.controllers = controllers

        self.app = FastAPI(
            title=self.config_reader.get("application.name", "MultiRAG Clean"),
            version=self.config_reader.get("application.version", "0.1.0"),
        )

        self.__register_exception_handlers()
        self.__register_controllers()

    def __register_exception_handlers(self) -> None:
        self.app.add_exception_handler(
            AppException,
            app_exception_handler,
        )

        self.app.add_exception_handler(
            RequestValidationError,
            validation_exception_handler,
        )

        self.app.add_exception_handler(
            StarletteHTTPException,
            http_exception_handler,
        )

        self.app.add_exception_handler(
            Exception,
            unhandled_exception_handler,
        )

    def __register_controllers(self) -> None:
        api_prefix = self.config_reader.get(
            "application.api_prefix",
            "/api/v1",
        )

        for controller in self.controllers:
            self.app.include_router(
                controller.api(),
                prefix=f"{api_prefix}{controller.route_prefix}",
            )

    async def init_database(self) -> None:
        db_context = InfrastructureCollection.db_context()

        await db_context.init_db()

    def start(self) -> None:
        host = self.config_reader.get(
            "application.host",
            "127.0.0.1"
        )
        port = int(
            self.config_reader.get(
                "application.port",
                8000,
            )
        )

        asyncio.run(self.init_database())

        uvicorn.run(
            self.app,
            host=host,
            port=port,
        )
