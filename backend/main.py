from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.jobs.scheduler import scheduler_service
from app.schemas.health import HealthStatusResponse
from app.scripts.seed_admin import seed_admin_user
from app.scripts.seed_demo import seed_demo_data
from app.services.health import HealthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await seed_admin_user()
    if settings.seed_demo_data:
        await seed_demo_data()
    await scheduler_service.start()
    try:
        yield
    finally:
        await scheduler_service.shutdown()


app = FastAPI(title="Agency CRM API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health", response_model=HealthStatusResponse)
async def healthcheck() -> HealthStatusResponse:
    return await HealthService().check_liveness()
