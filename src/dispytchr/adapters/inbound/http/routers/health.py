from fastapi import APIRouter

import dispytchr
from dispytchr.adapters.inbound.http.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=dispytchr.__version__)
