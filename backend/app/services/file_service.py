from __future__ import annotations

import uuid
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/bmp",
    "image/webp", "image/tiff",
}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/x-msvideo", "video/avi",
    "video/quicktime", "video/x-matroska", "video/webm",
}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def validate_image(filename: str, content_type: str | None, file_size: int) -> str | None:
    """Return error message if file is invalid, None if OK."""
    if file_size == 0:
        return "Empty file"
    if file_size > settings.MAX_IMAGE_SIZE:
        return f"File too large: {file_size / 1024 / 1024:.1f}MB (max {settings.MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB)"
    ext = Path(filename).suffix.lower()
    if content_type and content_type not in ALLOWED_IMAGE_TYPES:
        return f"Unsupported image type: {content_type}"
    if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
        return f"Unsupported extension: {ext}"
    return None


def validate_video(filename: str, content_type: str | None, file_size: int) -> str | None:
    """Return error message if file is invalid, None if OK."""
    if file_size == 0:
        return "Empty file"
    if file_size > settings.MAX_VIDEO_SIZE:
        return f"File too large: {file_size / 1024 / 1024:.1f}MB (max {settings.MAX_VIDEO_SIZE / 1024 / 1024 / 1024:.0f}GB)"
    ext = Path(filename).suffix.lower()
    if ext and ext not in ALLOWED_VIDEO_EXTENSIONS:
        return f"Unsupported extension: {ext}"
    # Ext is good — don't reject based on content_type alone (browsers vary)
    if content_type and ext in ALLOWED_VIDEO_EXTENSIONS:
        return None
    return None


def gen_filename(original_name: str) -> str:
    """Generate a UUID-based filename preserving the original extension."""
    ext = Path(original_name).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def save_upload(content: bytes, target_dir: Path, filename: str) -> Path:
    """Save uploaded file to disk. Returns the full saved path."""
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    path.write_bytes(content)
    return path


async def save_upload_stream(upload_file, target_dir: Path, filename: str, chunk_size: int = 1024 * 1024) -> tuple[Path, int]:
    """Stream an incoming UploadFile to disk in chunks.

    Reads the request body lazily (never loads the whole file into memory).
    Returns (saved_path, total_bytes_written).
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    total = 0
    with open(path, "wb") as f:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    return path, total


def path_to_url(full_path: Path) -> str:
    """Convert an absolute path to a URL path relative to uploads directory."""
    rel = full_path.relative_to(settings.UPLOAD_DIR)
    return f"/uploads/{rel.as_posix()}"


def cleanup_old_files(days: int = None):
    """Remove files older than `days` from upload directories."""
    if days is None:
        days = settings.CLEANUP_DAYS
    cutoff = datetime.now() - timedelta(days=days)
    for root_dir in [settings.UPLOAD_DIR / "images",
                     settings.UPLOAD_DIR / "videos",
                     settings.UPLOAD_DIR / "results"]:
        if not root_dir.exists():
            continue
        for path in root_dir.rglob("*"):
            if path.is_file():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        path.unlink()
                        logger.info("Cleaned up old file: %s", path)
                    except Exception:
                        pass
