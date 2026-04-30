from fastapi import APIRouter, Response, status

from app.schemas.health import HealthStatusResponse
from app.services.health import HealthService

router = APIRouter()


@router.get("/live", response_model=HealthStatusResponse)
async def liveness(response: Response) -> HealthStatusResponse:
    payload = await HealthService().check_liveness()
    if payload.status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


@router.get("/ready", response_model=HealthStatusResponse)
async def readiness(response: Response) -> HealthStatusResponse:
    payload = await HealthService().check_readiness()
    if payload.status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload
