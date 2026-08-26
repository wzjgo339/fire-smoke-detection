import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Float, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    annotated_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    image_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    total_count: Mapped[int] = mapped_column(Integer, default=0)
    smoke_count: Mapped[int] = mapped_column(Integer, default=0)
    fire_count: Mapped[int] = mapped_column(Integer, default=0)
    max_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    detections: Mapped[list["DetectionResult"]] = relationship(
        "DetectionResult", back_populates="record", cascade="all, delete-orphan"
    )


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_records.id", ondelete="CASCADE"), nullable=False)

    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_name: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x2: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y2: Mapped[float] = mapped_column(Float, nullable=False)

    frame_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    record: Mapped["DetectionRecord"] = relationship("DetectionRecord", back_populates="detections")


class VideoTask(Base):
    __tablename__ = "video_tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="processing")

    total_frames: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frames_processed: Mapped[int] = mapped_column(Integer, default=0)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    current_fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    annotated_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    total_detections: Mapped[int] = mapped_column(Integer, default=0)
    smoke_count: Mapped[int] = mapped_column(Integer, default=0)
    fire_count: Mapped[int] = mapped_column(Integer, default=0)
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    timeline_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    record_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
