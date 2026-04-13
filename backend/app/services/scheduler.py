from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self.scheduler.start()
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        self.scheduler.shutdown(wait=False)
        self._started = False


scheduler_service = SchedulerService()

