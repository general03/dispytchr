from fastapi import FastAPI

import dispytchr
from dispytchr.adapters.inbound.http.errors import register_exception_handlers
from dispytchr.adapters.inbound.http.routers import health
from dispytchr.application.use_cases import UseCases


def create_app(use_cases: UseCases) -> FastAPI:
    app = FastAPI(title="dispytchr", version=dispytchr.__version__)
    app.state.use_cases = use_cases

    register_exception_handlers(app)
    app.include_router(health.router)

    return app
