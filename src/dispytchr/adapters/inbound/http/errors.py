from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from dispytchr.domain.errors import DomainError

DOMAIN_ERROR_STATUS = HTTPStatus.UNPROCESSABLE_ENTITY


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=DOMAIN_ERROR_STATUS, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
