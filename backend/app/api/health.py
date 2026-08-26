import time

from fastapi import APIRouter

from ..schemas.common import HealthResponse
from ..services.detector import ModelManager
from ..utils.gpu_monitor import get_gpu_info

router = APIRouter()
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    model = ModelManager()
    return HealthResponse(
        status="ok" if model.is_loaded else "degraded",
        model=model.model_info,
        gpu=get_gpu_info(),
        uptime_seconds=round(time.time() - _start_time, 1),
        queue_size=0,
    )
