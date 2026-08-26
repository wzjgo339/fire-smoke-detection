import asyncio
import uuid
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query

from ..schemas.detection import (
    ImageDetectionResponse,
    VideoTaskStatusResponse,
    VideoTaskSubmitResponse,
)
from ..services.file_service import (
    validate_image,
    validate_video,
    gen_filename,
    path_to_url,
    save_upload_stream,
)
from ..services.image_service import process_image_path
from ..services.db_service import save_image_record
from ..services import video_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/detect/image", response_model=ImageDetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = Form(0.25),
    iou: float = Form(0.5),
):
    name = file.filename or "image.jpg"
    # Stream to a temp location first to validate size without loading into memory.
    from ..config import settings
    tmp_dir = settings.UPLOAD_DIR / "_tmp"
    tmp_name = gen_filename(name)
    tmp_path, size = await save_upload_stream(file, tmp_dir, tmp_name)

    err = validate_image(name, file.content_type, size)
    if err:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=err)

    record_id = uuid.uuid4().hex
    try:
        result = await process_image_path(
            file_path=tmp_path,
            original_filename=name,
            conf=confidence,
            iou=iou,
            record_id=record_id,
        )
    finally:
        # Remove the streamed temp file after decoding (the annotated result is saved elsewhere).
        tmp_path.unlink(missing_ok=True)
    try:
        await save_image_record(result)
    except Exception as e:
        logger.warning("Failed to save image record to DB: %s", e)
    return ImageDetectionResponse(**result)


@router.post("/detect/video", response_model=VideoTaskSubmitResponse)
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = Form(0.25),
    iou: float = Form(0.5),
    frame_skip: int = Form(1),
):
    from ..config import settings
    name = file.filename or "video.mp4"
    tmp_dir = settings.UPLOAD_DIR / "_tmp"
    tmp_path, size = await save_upload_stream(file, tmp_dir, gen_filename(name))

    err = validate_video(name, file.content_type, size)
    if err:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=err)

    task_id = uuid.uuid4().hex

    # Launch background processing (the streamed temp file is moved into place there).
    asyncio.create_task(
        video_service.process_video(
            file_path=tmp_path,
            original_filename=name,
            conf=confidence,
            iou=iou,
            frame_skip=frame_skip,
            task_id=task_id,
        )
    )

    return VideoTaskSubmitResponse(
        task_id=task_id,
        status="processing",
        filename=name,
        total_frames=None,
        estimated_seconds=None,
        created_at=None,
    )


@router.get("/detect/video/{task_id}", response_model=VideoTaskStatusResponse)
async def get_video_status(task_id: str):
    task = await video_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return VideoTaskStatusResponse(**task)
