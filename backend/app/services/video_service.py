from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
from sqlalchemy import select

from ..config import settings
from ..database import async_session
from ..models.detection import VideoTask
from ..utils.chinese_path import imwrite
from ..utils.visualization import draw_detections
from .detector import ModelManager
from .file_service import gen_filename, path_to_url, save_upload

logger = logging.getLogger(__name__)

# In-memory task state for video processing (hot cache; DB is the source of truth
# for survival across restarts).
_video_tasks: dict[str, dict] = {}


async def _persist_task(task_id: str, data: dict) -> None:
    """Upsert a video task snapshot into the VideoTask table."""
    try:
        async with async_session() as db:
            row = (await db.execute(
                select(VideoTask).where(VideoTask.task_id == task_id)
            )).scalar_one_or_none()

            timeline_json = json.dumps(data.get("timeline", []), ensure_ascii=False)
            results_json = json.dumps(data.get("results", []), ensure_ascii=False)

            created_at = data.get("created_at")
            if created_at is not None:
                if isinstance(created_at, (int, float)):
                    created_at = datetime.fromtimestamp(created_at, tz=timezone.utc)
                elif isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
            else:
                created_at = datetime.now(timezone.utc)

            fields = dict(
                filename=data.get("filename"),
                original_path=data.get("original_path"),
                status=data.get("status", "processing"),
                total_frames=data.get("total_frames"),
                frames_processed=data.get("frames_processed"),
                progress_pct=data.get("progress_pct", 0.0),
                current_fps=data.get("current_fps"),
                annotated_path=data.get("annotated_path"),
                total_detections=data.get("total_detections", 0),
                smoke_count=data.get("smoke_count", 0),
                fire_count=data.get("fire_count", 0),
                processing_time_ms=data.get("processing_time_ms"),
                timeline_json=timeline_json,
                results_json=results_json,
                error_message=data.get("error"),
                created_at=created_at,
            )

            if row is None:
                db.add(VideoTask(task_id=task_id, **fields))
            else:
                for k, v in fields.items():
                    setattr(row, k, v)
            await db.commit()
    except Exception as e:
        logger.warning("Failed to persist video task snapshot: %s", e)


def _task_to_dict(row: VideoTask) -> dict:
    """Convert a VideoTask DB row to the dict shape expected by the status API."""
    return {
        "task_id": row.task_id,
        "status": row.status,
        "filename": row.filename,
        "progress_pct": row.progress_pct,
        "frames_processed": row.frames_processed,
        "frames_total": row.total_frames,
        "current_fps": row.current_fps,
        "annotated_url": path_to_url(Path(row.annotated_path)) if row.annotated_path else None,
        "original_url": path_to_url(Path(row.original_path)) if row.original_path else None,
        "duration_seconds": None,
        "total_frames": row.total_frames,
        "total_detections": row.total_detections,
        "smoke_count": row.smoke_count,
        "fire_count": row.fire_count,
        "processing_time_ms": row.processing_time_ms,
        "results": json.loads(row.results_json) if row.results_json else [],
        "timeline": json.loads(row.timeline_json) if row.timeline_json else [],
        "error": row.error_message,
        "created_at": row.created_at,
    }


async def get_task(task_id: str) -> dict | None:
    """Return a video task snapshot.

    Live tasks are served from the in-memory cache; anything not found there is
    loaded from the database. A task still tagged 'processing' in the DB after a
    restart (i.e. not present in the cache) is reported as failed, since its
    background worker is gone.
    """
    cached = _video_tasks.get(task_id)
    if cached is not None:
        # Normalize to the status-API shape (ensure frames_total etc. are present).
        return {
            **cached,
            "frames_total": cached.get("frames_total", cached.get("total_frames")),
            "duration_seconds": None,
        }
    try:
        async with async_session() as db:
            row = (await db.execute(
                select(VideoTask).where(VideoTask.task_id == task_id)
            )).scalar_one_or_none()
    except Exception as e:
        logger.warning("Failed to load video task from DB: %s", e)
        return None
    if row is None:
        return None
    data = _task_to_dict(row)
    if data["status"] == "processing":
        # Worker is gone after a restart -> mark as interrupted/failed.
        data["status"] = "failed"
        data["error"] = "任务因服务重启被中断"
    return data


async def process_video(
    original_filename: str,
    conf: float = 0.25,
    iou: float = 0.5,
    frame_skip: int = 1,
    task_id: str | None = None,
    file_path: Path | str | None = None,
    file_bytes: bytes | None = None,
):
    """Background video processing: save, decode frame-by-frame, detect, annotate, assemble.

    The uploaded video is read from ``file_path`` (a streamed temp file); it is moved
    into the persistent uploads/videos dir, then decoded and processed frame by frame.
    """
    import uuid as _uuid
    if task_id is None:
        task_id = _uuid.uuid4().hex

    t_start = time.perf_counter()

    filename = gen_filename(original_filename)
    if file_path is not None:
        # Move the streamed temp file into the persistent videos directory.
        src = Path(file_path)
        dst = settings.UPLOAD_DIR / "videos" / filename
        if src != dst:
            try:
                import shutil
                shutil.move(str(src), str(dst))
            except Exception:
                # Fall back to copy if the temp file was already cleaned up.
                shutil.copy(str(src), str(dst))
        original_path = dst
    else:
        # Legacy path (in-memory bytes) kept for backward compatibility.
        original_path = save_upload(file_bytes, settings.UPLOAD_DIR / "videos", filename)

    cap = cv2.VideoCapture(str(original_path))
    if not cap.isOpened():
        _video_tasks[task_id] = {
            "task_id": task_id, "status": "failed", "filename": original_filename,
            "error": "Cannot open video file",
        }
        await _persist_task(task_id, _video_tasks[task_id])
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if settings.MAX_VIDEO_FRAMES > 0:
        total_frames = min(total_frames, settings.MAX_VIDEO_FRAMES)

    estimated = (total_frames / frame_skip) * 0.005 if fps > 0 else None

    _video_tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "filename": original_filename,
        "original_path": str(original_path),
        "total_frames": total_frames,
        "frames_total": total_frames,
        "frames_processed": 0,
        "progress_pct": 0.0,
        "current_fps": 0.0,
        "estimated_seconds": estimated,
        "created_at": datetime.now(timezone.utc),
    }
    await _persist_task(task_id, _video_tasks[task_id])

    # Always output .mp4 for browser compatibility
    out_ext = ".mp4"
    out_filename = f"{Path(filename).stem}_annotated{out_ext}"
    out_dir = settings.UPLOAD_DIR / "results" / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_filename

    # Try H.264 codecs for best browser compatibility
    fourcc_candidates = [
        cv2.VideoWriter_fourcc(*"avc1"),
        cv2.VideoWriter_fourcc(*"H264"),
        cv2.VideoWriter_fourcc(*"mp4v"),
    ]
    out = None
    for fourcc in fourcc_candidates:
        out = cv2.VideoWriter(str(out_path), fourcc, fps, (frame_w, frame_h))
        if out.isOpened():
            break
        out = None

    if out is None:
        _video_tasks[task_id] = {
            "task_id": task_id, "status": "failed", "filename": original_filename,
            "error": "Cannot create output video (no compatible codec)",
        }
        await _persist_task(task_id, _video_tasks[task_id])
        cap.release()
        return

    model = ModelManager()
    all_frame_results = []
    timeline_points = []
    timeline_interval = max(1, int(fps * 5)) if fps > 0 else 150  # ~every 5 seconds
    frame_idx = 0
    processed = 0
    total_detections = 0
    smoke_count = 0
    fire_count = 0
    last_progress_update = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        is_detected_frame = (frame_idx % frame_skip == 0)
        if is_detected_frame:
            processed += 1
            detections = await model.detect(frame, conf=conf, iou=iou)
            # Cache last detections so skipped frames reuse the nearest annotation.
            last_detections = detections
        else:
            # Skipped frame: reuse the most recent detection result to avoid a
            # flickering mixture of annotated/blank frames in the output video.
            detections = last_detections if last_detections else []

        # Only record per-frame results for actually-detected frames (not skips).
        if is_detected_frame and detections:
            all_frame_results.append({
                "frame_index": frame_idx,
                "timestamp_sec": round(frame_idx / fps, 2) if fps > 0 else None,
                "detections": detections,
                "count": len(detections),
            })
            total_detections += len(detections)
            smoke_count += sum(1 for d in detections if d["class_id"] == 0)
            fire_count += sum(1 for d in detections if d["class_id"] == 1)

        if frame_idx % timeline_interval == 0:
            timeline_points.append({
                "t": round(frame_idx / fps, 1) if fps > 0 else frame_idx,
                "count": sum(r["count"] for r in all_frame_results[-10:]),
            })

        annotated = draw_detections(frame, detections)
        out.write(annotated)

        # Update progress every 100 frames
        if processed - last_progress_update >= 100:
            elapsed = time.perf_counter() - t_start
            _video_tasks[task_id].update({
                "frames_processed": processed,
                "progress_pct": round(processed / max(total_frames, 1) * 100, 1),
                "current_fps": round(processed / elapsed, 1) if elapsed > 0 else 0,
            })
            await _persist_task(task_id, _video_tasks[task_id])
            last_progress_update = processed

        frame_idx += 1

    cap.release()
    out.release()
    elapsed_ms = (time.perf_counter() - t_start) * 1000

    task_data = {
        "task_id": task_id,
        "status": "completed",
        "filename": original_filename,
        "original_path": str(original_path),
        "annotated_path": str(out_path),
        "annotated_url": path_to_url(out_path),
        "original_url": path_to_url(original_path),
        "total_frames": total_frames,
        "frames_processed": processed,
        "progress_pct": 100.0,
        "total_detections": total_detections,
        "smoke_count": smoke_count,
        "fire_count": fire_count,
        "processing_time_ms": round(elapsed_ms, 2),
        "results": all_frame_results[:500],
        "timeline": timeline_points,
        "duration_seconds": round(total_frames / fps, 2) if fps and fps > 0 else None,
        "created_at": datetime.now(timezone.utc),
    }
    _video_tasks[task_id].update(task_data)
    await _persist_task(task_id, task_data)

    try:
        from .db_service import save_video_record
        await save_video_record(task_data)
    except Exception as e:
        logger.warning("Failed to save video record to DB: %s", e)
