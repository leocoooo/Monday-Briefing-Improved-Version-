from contextlib import asynccontextmanager
from monday_report.core.scheduler import scheduler
from monday_report.services.briefing_service import BriefingService
from monday_report.services.email_service import EmailService

async def scheduled_monday_job():
    print("Lancement du briefing hebdomadaire...")
    report = await BriefingService.build_report()
    result = EmailService.send_email("Briefing Hebdomadaire", report)
    print("Envoi effectué :", result)


@asynccontextmanager
async def lifespan(app):
    scheduler.add_job(
        scheduled_monday_job,
        'cron',
        day_of_week='mon',
        hour=8,
        minute=0,
        id='monday_briefing'
    )
    scheduler.start()
    print(f"Scheduler démarré ({scheduler.timezone})")
    yield
    scheduler.shutdown()
    print("Scheduler arrêté")
