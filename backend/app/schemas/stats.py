from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_records: int = 0
    total_images: int = 0
    total_videos: int = 0
    total_detections: int = 0
    total_fire: int = 0
    total_smoke: int = 0
    today_count: int = 0
    detections_by_day: list[dict] = []
    confidence_distribution: dict[str, int] = {}
    class_pie: dict[str, int] = {}
    avg_confidence_fire: float | None = None
    avg_confidence_smoke: float | None = None
    recent_activity: list[dict] = []
