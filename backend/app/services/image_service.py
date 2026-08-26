from __future__ import annotations

import logging
import time
from pathlib import Path

import cv2
import numpy as np

from ..config import settings
from ..utils.chinese_path import imread, imwrite
from ..utils.visualization import draw_detections
from .detector import ModelManager
from .file_service import gen_filename, path_to_url, save_upload

logger = logging.getLogger(__name__)


async def _process_image_common(
    img: np.ndarray,
    original_filename: str,
    original_path: Path,
    conf: float,
    iou: float,
    record_id: str | None,
) -> dict:
    """Shared image pipeline after the image has been decoded and saved."""
    t0 = time.perf_counter()
    h, w = img.shape[:2]

    model = ModelManager()
    detections = await model.detect(img, conf=conf, iou=iou)

    annotated = draw_detections(img.copy(), detections)
    result_filename = f"{Path(original_path.stem).stem}_annotated.jpg"
    result_dir = settings.UPLOAD_DIR / "results" / "images"
    result_dir.mkdir(parents=True, exist_ok=True)
    result_path = result_dir / result_filename
    imwrite(str(result_path), annotated)

    thumb = cv2.resize(annotated, (300, int(300 * h / w))) if w > 0 else annotated
    thumb_filename = f"{Path(original_path.stem).stem}_thumb.jpg"
    thumb_dir = settings.UPLOAD_DIR / "results" / "thumbs"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = thumb_dir / thumb_filename
    imwrite(str(thumb_path), thumb)

    elapsed = (time.perf_counter() - t0) * 1000

    smoke_count = sum(1 for d in detections if d["class_id"] == 0)
    fire_count = sum(1 for d in detections if d["class_id"] == 1)
    max_conf = max((d["confidence"] for d in detections), default=None)

    result = {
        "id": record_id or original_path.stem,
        "filename": original_filename,
        "original_url": path_to_url(original_path),
        "annotated_url": path_to_url(result_path),
        "thumbnail_url": path_to_url(thumb_path),
        "detections": detections,
        "total_count": len(detections),
        "smoke_count": smoke_count,
        "fire_count": fire_count,
        "max_confidence": max_conf,
        "processing_time_ms": round(elapsed, 2),
        "image_width": w,
        "image_height": h,
    }
    return result


async def process_image_path(
    file_path: Path | str,
    original_filename: str,
    conf: float = 0.25,
    iou: float = 0.5,
    record_id: str | None = None,
) -> dict:
    """Full image detection pipeline from a file on disk (streamed upload).

    The uploaded file is decoded from disk, detected, annotated, and the annotated
    result plus thumbnail are saved. The source file is left in place.
    """
    file_path = Path(file_path)
    img = imread(file_path)
    if img is None:
        raise ValueError("Failed to decode image")
    return await _process_image_common(
        img, original_filename, file_path, conf, iou, record_id
    )


async def process_image(
    file_bytes: bytes,
    original_filename: str,
    conf: float = 0.25,
    iou: float = 0.5,
    record_id: str | None = None,
) -> dict:
    """Full image detection pipeline from an in-memory byte buffer.

    Kept for backward compatibility; decodes the buffer, saves the original, then
    runs the same common pipeline.
    """
    from ..utils.chinese_path import imdecode

    img = imdecode(file_bytes)
    if img is None:
        raise ValueError("Failed to decode image")

    filename = gen_filename(original_filename)
    original_path = save_upload(file_bytes, settings.UPLOAD_DIR / "images", filename)

    return await _process_image_common(
        img, original_filename, original_path, conf, iou, record_id
    )
