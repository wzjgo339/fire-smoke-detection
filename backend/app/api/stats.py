from fastapi import APIRouter

from ..schemas.stats import DashboardStats
from ..services.stats_service import get_dashboard_stats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def stats():
    data = await get_dashboard_stats()
    return DashboardStats(**data)
