from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, delete, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.detection import DetectionRecord, DetectionResult
from ..schemas.history import HistoryItem, HistoryDetail, PaginatedHistory

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=PaginatedHistory)
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, description="image or video"),
    search: str | None = Query(None),
    has_detections: bool | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    q = select(DetectionRecord)

    if type:
        q = q.where(DetectionRecord.type == type)
    if search:
        q = q.where(DetectionRecord.filename.ilike(f"%{search}%"))
    if has_detections is True:
        q = q.where(DetectionRecord.total_count > 0)
    elif has_detections is False:
        q = q.where(DetectionRecord.total_count == 0)

    # Sort
    sort_col = getattr(DetectionRecord, sort_by, DetectionRecord.created_at)
    if sort_order == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    # Count
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    q = q.offset(offset).limit(page_size)
    rows = (await db.execute(q)).scalars().all()

    def _make_url(p: str | None) -> str | None:
        if not p:
            return None
        return f"/uploads/{p}" if not p.startswith("/uploads/") else p

    items = [
        HistoryItem(
            id=r.id,
            type=r.type,
            filename=r.filename,
            thumbnail_url=_make_url(r.thumbnail_path),
            total_detections=r.total_count,
            smoke_count=r.smoke_count,
            fire_count=r.fire_count,
            max_confidence=r.max_confidence,
            processing_time_ms=r.processing_time_ms,
            created_at=r.created_at.replace(tzinfo=None) if r.created_at else None,
        )
        for r in rows
    ]

    return PaginatedHistory(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/history/{record_id}", response_model=HistoryDetail)
async def get_history_detail(record_id: str, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(
        select(DetectionRecord).where(DetectionRecord.id == record_id)
    )).scalar_one_or_none()
    if r is None:
        raise HTTPException(status_code=404, detail="Record not found")

    dets = (await db.execute(
        select(DetectionResult).where(DetectionResult.record_id == record_id)
    )).scalars().all()

    def _make_url(p: str | None) -> str | None:
        if not p:
            return None
        if "\\uploads\\" in p:
            return "/" + p.split("\\uploads\\", 1)[1].replace("\\", "/")
        if "/uploads/" in p:
            return p
        return None

    return HistoryDetail(
        id=r.id,
        type=r.type,
        filename=r.filename,
        thumbnail_url=_make_url(r.thumbnail_path),
        original_url=_make_url(r.original_path),
        annotated_url=_make_url(r.annotated_path),
        image_width=r.image_width,
        image_height=r.image_height,
        total_detections=r.total_count,
        smoke_count=r.smoke_count,
        fire_count=r.fire_count,
        max_confidence=r.max_confidence,
        processing_time_ms=r.processing_time_ms,
        created_at=r.created_at.replace(tzinfo=None) if r.created_at else None,
        detections=[
            {
                "bbox": [d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2],
                "class": d.class_name,
                "class_id": d.class_id,
                "confidence": d.confidence,
                "frame_index": d.frame_index,
                "timestamp_sec": d.timestamp_sec,
            }
            for d in dets
        ],
    )


@router.delete("/history/{record_id}")
async def delete_history(record_id: str, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(
        select(DetectionRecord).where(DetectionRecord.id == record_id)
    )).scalar_one_or_none()
    if r is None:
        raise HTTPException(status_code=404, detail="Record not found")

    await db.delete(r)
    await db.commit()
    return {"ok": True}
