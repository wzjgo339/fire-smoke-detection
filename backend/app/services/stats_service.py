from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, select, case

from ..database import async_session
from ..models.detection import DetectionRecord, DetectionResult

logger = logging.getLogger(__name__)


def _make_url(p: str | None) -> str | None:
    if not p:
        return None
    return f"/uploads/{p}" if not p.startswith("/uploads/") else p


async def get_dashboard_stats() -> dict:
    async with async_session() as db:
        # Total counts
        total_records_result = await db.execute(select(func.count(DetectionRecord.id)))
        total_records = total_records_result.scalar()

        total_images_result = await db.execute(
            select(func.count(DetectionRecord.id)).where(DetectionRecord.type == "image")
        )
        total_images = total_images_result.scalar()

        total_videos_result = await db.execute(
            select(func.count(DetectionRecord.id)).where(DetectionRecord.type == "video")
        )
        total_videos = total_videos_result.scalar()

        # Today's count
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await db.execute(
            select(func.count(DetectionRecord.id)).where(DetectionRecord.created_at >= today)
        )
        today_count = today_result.scalar()

        # Aggregate detection counts
        total_detections_result = await db.execute(
            select(func.sum(DetectionRecord.total_count))
        )
        total_detections = total_detections_result.scalar() or 0

        total_fire_result = await db.execute(
            select(func.sum(DetectionRecord.fire_count))
        )
        total_fire = total_fire_result.scalar() or 0

        total_smoke_result = await db.execute(
            select(func.sum(DetectionRecord.smoke_count))
        )
        total_smoke = total_smoke_result.scalar() or 0

        # Detections by day (last 14 days). SQLite `date()` works on ISO strings.
        since = (now - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0)
        by_day_rows = (
            await db.execute(
                select(
                    func.date(DetectionRecord.created_at).label("day"),
                    func.count(DetectionRecord.id),
                )
                .where(DetectionRecord.created_at >= since)
                .group_by("day")
                .order_by("day")
            )
        ).all()
        detections_by_day = [{"date": day, "count": cnt} for day, cnt in by_day_rows]

        # Confidence distribution (buckets of 0.1) across all detection results.
        conf_rows = (
            await db.execute(
                select(
                    func.floor(DetectionResult.confidence * 10).label("bucket"),
                    func.count(DetectionResult.id),
                )
                .group_by("bucket")
                .order_by("bucket")
            )
        ).all()
        # e.g. bucket=8.0 -> key "0.8" (confidence interval [0.8, 0.9)).
        confidence_distribution = {f"{float(b) / 10.0:.1f}": int(c) for b, c in conf_rows}

        # Average confidence per class, from stored detection results.
        avg_rows = (
            await db.execute(
                select(
                    DetectionResult.class_id,
                    func.avg(DetectionResult.confidence),
                ).group_by(DetectionResult.class_id)
            )
        ).all()
        avg_map = {class_id: float(avg) for class_id, avg in avg_rows if avg is not None}

        # Recent activity
        recent_result = await db.execute(
            select(DetectionRecord)
            .order_by(DetectionRecord.created_at.desc())
            .limit(10)
        )
        recent = [
            {
                "id": r.id,
                "type": r.type,
                "filename": r.filename,
                "detection_count": r.total_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "thumbnail_url": _make_url(r.thumbnail_path),
            }
            for r in recent_result.scalars().all()
        ]

        return {
            "total_records": total_records,
            "total_images": total_images,
            "total_videos": total_videos,
            "total_detections": int(total_detections),
            "total_fire": int(total_fire),
            "total_smoke": int(total_smoke),
            "today_count": today_count,
            "detections_by_day": detections_by_day,
            "confidence_distribution": confidence_distribution,
            "class_pie": {"fire": int(total_fire), "smoke": int(total_smoke)},
            "avg_confidence_fire": avg_map.get(1),
            "avg_confidence_smoke": avg_map.get(0),
            "recent_activity": recent,
        }
