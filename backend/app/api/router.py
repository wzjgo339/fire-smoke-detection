from fastapi import APIRouter

from .health import router as health_router
from .detection import router as detection_router
from .history import router as history_router
from .stats import router as stats_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(detection_router)
api_router.include_router(history_router)
api_router.include_router(stats_router)
