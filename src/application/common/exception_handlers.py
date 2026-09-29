import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.application.common.dtos.error_response_dto import ErrorResponseDto
from src.core.exceptions.app_exception import AppException


logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    response = ErrorResponseDto(
        message=exc.message,
        errors=exc.errors,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    response = ErrorResponseDto(
        message="Validation error",
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    response = ErrorResponseDto(
        message=str(exc.detail),
        errors=None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled exception for %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    response = ErrorResponseDto(
        message="Internal server error",
        errors=None,
    )

    return JSONResponse(
        status_code=500,
        content=response.model_dump(),
    )
