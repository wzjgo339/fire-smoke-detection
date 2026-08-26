from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path


def imread(path: str | Path) -> np.ndarray | None:
    """Read image from a path that may contain non-ASCII characters.
    cv2.imread silently returns None for paths with Chinese characters."""
    p = str(Path(path).resolve())
    buf = np.fromfile(p, dtype=np.uint8)
    if buf.size == 0:
        return None
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def imwrite(path: str | Path, img: np.ndarray, params: list[int] | None = None) -> bool:
    """Write image to a path that may contain non-ASCII characters."""
    p = str(Path(path).resolve())
    ext = Path(p).suffix.lower()
    if not ext:
        ext = ".jpg"
    success, buf = cv2.imencode(ext, img, params or [])
    if not success:
        return False
    buf.tofile(p)
    return True


def imdecode(buf: bytes) -> np.ndarray | None:
    """Decode image from bytes buffer (in-memory)."""
    arr = np.frombuffer(buf, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def imencode(img: np.ndarray, ext: str = ".jpg", quality: int = 95) -> bytes | None:
    """Encode image to bytes buffer."""
    success, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        return None
    return buf.tobytes()
