from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import AsyncSessionLocal
from app.services.fb_sync import FacebookSyncService
from app.services.usdt import USDTService


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._configured = False

    def _configure(self) -> None:
        if self._configured:
            return
        self.scheduler.add_job(self.run_fb_sync, IntervalTrigger(minutes=15), id="facebook-sync", replace_existing=True)
        self.scheduler.add_job(self.run_usdt_poll, IntervalTrigger(minutes=5), id="usdt-poll", replace_existing=True)
        self._configured = True

    async def start(self) -> None:
        self._configure()
        if not self.scheduler.running:
            self.scheduler.start()

    async def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def run_fb_sync(self) -> dict[str, int]:
        async with AsyncSessionLocal() as session:
            return await FacebookSyncService(session).sync_accounts()

    async def run_usdt_poll(self) -> dict[str, int]:
        async with AsyncSessionLocal() as session:
            return await USDTService(session).poll_transactions()


scheduler_service = SchedulerService()

