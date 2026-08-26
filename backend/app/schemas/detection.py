from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    model: dict
    gpu: dict
    uptime_seconds: float
    queue_size: int


class ErrorResponse(BaseModel):
    error: dict  # { code: str, message: str, details: dict }
    request_id: str | None = None


class DetectionOut(BaseModel):
    bbox: list[float]  # [x1, y1, x2, y2]
    class_name: str = Field(alias="class")
    class_id: int
    confidence: float

    class Config:
        populate_by_name = True


class ImageDetectionResponse(BaseModel):
    id: str
    filename: str
    original_url: str
    annotated_url: str | None = None
    thumbnail_url: str | None = None
    detections: list[DetectionOut] = []
    total_count: int = 0
    smoke_count: int = 0
    fire_count: int = 0
    max_confidence: float | None = None
    processing_time_ms: float | None = None
    image_width: int | None = None
    image_height: int | None = None


class VideoTaskSubmitResponse(BaseModel):
    task_id: str
    status: str
    filename: str
    total_frames: int | None = None
    estimated_seconds: float | None = None
    created_at: datetime | None = None


class FrameDetection(BaseModel):
    frame_index: int
    timestamp_sec: float | None = None
    detections: list[DetectionOut] = []
    count: int = 0


class TimelinePoint(BaseModel):
    t: float
    count: int


class VideoTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress_pct: float | None = None
    frames_processed: int | None = None
    frames_total: int | None = None
    current_fps: float | None = None
    filename: str | None = None
    annotated_url: str | None = None
    original_url: str | None = None
    duration_seconds: float | None = None
    total_frames: int | None = None
    total_detections: int | None = None
    smoke_count: int | None = None
    fire_count: int | None = None
    processing_time_ms: float | None = None
    results: list[FrameDetection] | None = None
    timeline: list[TimelinePoint] | None = None
    error: str | None = None
    created_at: datetime | None = None
