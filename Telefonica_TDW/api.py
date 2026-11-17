import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from controllers.failure_report_controller import router as failure_report_router
from controllers.recharge_controller import router as recharge_router
from models.failure_report import initialize_failure_report_table
from models.recharge import initialize_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    initialize_failure_report_table()
    yield


app = FastAPI(title="Telefónica Prepago Recharge API", lifespan=lifespan)
app.include_router(recharge_router, prefix="/api/v1/recharges", tags=["recharges"])
app.include_router(failure_report_router, prefix="/api/v1/reports")


def problem_response(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        headers=headers,
        content={
            "type": "about:blank",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": request.url.path,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    try:
        title = HTTPStatus(exc.status_code).phrase
    except ValueError:
        title = "HTTP Error"
    detail = exc.detail if isinstance(exc.detail, str) else "The request failed."
    return problem_response(
        request,
        exc.status_code,
        title,
        detail,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, _: RequestValidationError
) -> JSONResponse:
    return problem_response(
        request,
        400,
        "Bad Request",
        "The request payload is invalid.",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error", exc_info=exc)
    return problem_response(
        request,
        500,
        "Internal Server Error",
        "The request could not be completed.",
    )
