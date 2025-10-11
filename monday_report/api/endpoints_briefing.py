from fastapi import APIRouter, BackgroundTasks
from monday_report.services.briefing_service import BriefingService

from monday_report.services.email_service import EmailService
from monday_report.models.common import ReportResponse


router = APIRouter(prefix="", tags=["briefing"])


@router.get("/monday-report", response_model=ReportResponse)

async def monday_report(background_tasks: BackgroundTasks):

    report = await BriefingService.build_report()

    background_tasks.add_task(EmailService.send_email, "Briefing Hebdomadaire", report)

    return ReportResponse(status="scheduled_send", preview=report[:800],

                          full_report=report if len(report) <= 800 else None)

