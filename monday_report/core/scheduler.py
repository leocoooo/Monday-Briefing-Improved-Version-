from apscheduler.schedulers.asyncio import AsyncIOScheduler
from monday_report.core.config import settings

scheduler = AsyncIOScheduler(timezone=settings.timezone)