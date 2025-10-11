from fastapi import APIRouter
from monday_report.services.briefing_service import BriefingService
from monday_report.services.email_service import EmailService

router = APIRouter(prefix="", tags=["test"])

@router.get("/test-now")
async def test_now():
    report = await BriefingService.build_report()
    result = EmailService.send_email("Test Briefing", report)
    return {"status": "executed", "email_result": result, "full_report": report}
