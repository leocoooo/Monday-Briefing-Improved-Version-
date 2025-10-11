from pydantic import BaseModel
from datetime import datetime
import pytz
from monday_report.core.config import settings

class ReportResponse(BaseModel):
    status: str
    preview: str
    full_report: str | None = None


class HealthResponse(BaseModel):
    status: str
    time: str

    @staticmethod
    def build():
        tz = pytz.timezone(settings.timezone)
        return HealthResponse(status="ok", time=datetime.now(tz).isoformat())
