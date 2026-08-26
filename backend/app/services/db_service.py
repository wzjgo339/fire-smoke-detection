from __future__ import annotations

"""Database persistence for detection records."""
import logging

from ..database import async_session
from ..models.detection import DetectionRecord, DetectionResult

logger = logging.getLogger(__name__)


def _url_to_rel(url: str | None) -> str | None:
    """Convert /uploads/... URL back to relative path for storage."""
    if not url:
        return None
    return url.replace("/uploads/", "", 1) if url.startswith("/uploads/") else url


async def save_image_record(result: dict) -> None:
    """Save an image detection result to the database."""
    async with async_session() as db:
        record = DetectionRecord(
            id=result["id"],
            type="image",
            filename=result["filename"],
            original_path=_url_to_rel(result.get("original_url")),
            annotated_path=_url_to_rel(result.get("annotated_url")),
            thumbnail_path=_url_to_rel(result.get("thumbnail_url")),
            image_width=result.get("image_width"),
            image_height=result.get("image_height"),
            total_count=result["total_count"],
            smoke_count=result["smoke_count"],
            fire_count=result["fire_count"],
            max_confidence=result.get("max_confidence"),
            processing_time_ms=result.get("processing_time_ms"),
        )
        db.add(record)

        for det in result.get("detections", []):
            bbox = det["bbox"]
            db.add(DetectionResult(
                record_id=result["id"],
                class_id=det["class_id"],
                class_name=det["class"],
                confidence=det["confidence"],
                bbox_x1=bbox[0], bbox_y1=bbox[1], bbox_x2=bbox[2], bbox_y2=bbox[3],
            ))

        await db.commit()


async def save_video_record(task: dict) -> None:
    """Save a completed video detection result to the database."""
    async with async_session() as db:
        record = DetectionRecord(
            id=task["task_id"],
            type="video",
            filename=task.get("filename", "unknown"),
            original_path=_url_to_rel(task.get("original_url")),
            annotated_path=_url_to_rel(task.get("annotated_url")),
            total_count=task.get("total_detections", 0),
            smoke_count=task.get("smoke_count", 0),
            fire_count=task.get("fire_count", 0),
            processing_time_ms=task.get("processing_time_ms"),
        )
        db.add(record)

        for frame_result in task.get("results", []):
            for det in frame_result.get("detections", []):
                bbox = det["bbox"]
                db.add(DetectionResult(
                    record_id=task["task_id"],
                    class_id=det["class_id"],
                    class_name=det["class"],
                    confidence=det["confidence"],
                    bbox_x1=bbox[0], bbox_y1=bbox[1], bbox_x2=bbox[2], bbox_y2=bbox[3],
                    frame_index=frame_result.get("frame_index"),
                    timestamp_sec=frame_result.get("timestamp_sec"),
                ))

        await db.commit()
