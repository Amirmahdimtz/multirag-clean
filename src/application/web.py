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
from src.core.exceptions.app_exception import AppException
from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.db_context import DbContext


class WebService:
    def __init__(
        self,
        config_reader: ConfigReader,
        controllers: Sequence[BaseController],
        db_context: DbContext,
    ) -> None:
        self.config_reader = config_reader
        self.controllers = controllers
        self.db_context = db_context

        self.app = FastAPI(
            title=self.config_reader.require("application.name"),
            version=self.config_reader.require("application.version"),
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
        api_prefix = self.config_reader.require("application.api_prefix")
        api_prefix = self.__normalize_prefix(api_prefix)

        registered_prefixes: set[str] = set()

        for controller in self.controllers:
            route_prefix = self.__normalize_prefix(controller.route_prefix)
            full_prefix = f"{api_prefix}{route_prefix}"

            if full_prefix in registered_prefixes:
                raise ValueError(
                    f"Duplicate controller route prefix detected: {full_prefix}"
                )

            registered_prefixes.add(full_prefix)

            self.app.include_router(
                controller.api(),
                prefix=full_prefix,
            )

    def __normalize_prefix(self, prefix: str) -> str:
        if not prefix:
            return ""

        normalized = prefix.strip()

        if not normalized.startswith("/"):
            normalized = f"/{normalized}"

        return normalized.rstrip("/")

    async def init_database(self) -> None:

        await self.db_context.init_db()

    def start(self) -> None:
        host = self.config_reader.get(
            "application.host",
        )
        port = int(
            self.config_reader.get(
                "application.port",
            )
        )

        asyncio.run(self.init_database())

        uvicorn.run(
            self.app,
            host=host,
            port=port,
        )
