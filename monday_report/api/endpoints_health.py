from fastapi import APIRouter
from monday_report.models.common import HealthResponse

router = APIRouter(prefix="", tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse.build()
