from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: str
    type: str
    filename: str
    thumbnail_url: str | None = None
    total_detections: int = 0
    smoke_count: int = 0
    fire_count: int = 0
    max_confidence: float | None = None
    processing_time_ms: float | None = None
    created_at: datetime | None = None


class HistoryDetail(HistoryItem):
    original_url: str | None = None
    annotated_url: str | None = None
    image_width: int | None = None
    image_height: int | None = None
    detections: list = []


class PaginatedHistory(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int
