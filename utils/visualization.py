"""Detection result visualization utilities."""

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# BGR color map for OpenCV
color_map = {
    "fire": (0, 0, 255),    # Red
    "smoke": (0, 165, 255), # Orange
}


def draw_detections(
    image: np.ndarray,
    detections: list[dict],
    conf_threshold: float = 0.0,
    line_width: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
    """Draw bounding boxes with class labels and confidence scores.

    Args:
        image: BGR image as numpy array.
        detections: List of dicts with keys: bbox [x1,y1,x2,y2], class, confidence.
        conf_threshold: Only draw detections above this confidence.
        line_width: Bounding box line width.
        font_scale: Label text scale.

    Returns:
        Annotated image (copy, original unchanged).
    """
    canvas = image.copy()
    for det in detections:
        conf = det.get("confidence", 0)
        if conf < conf_threshold:
            continue
        cls_name = det.get("class", "unknown")
        bbox = det["bbox"]
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        color = color_map.get(cls_name, (255, 255, 255))

        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, line_width)

        label = f"{cls_name} {conf:.2f}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
        cv2.rectangle(canvas, (x1, y1 - th - baseline - 4), (x1 + tw, y1), color, -1)
        cv2.putText(canvas, label, (x1, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    return canvas


def save_result_image(image: np.ndarray, output_path: Path, detections: list[dict] = None):
    """Save an annotated image to disk. Creates parent directories if needed."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = draw_detections(image, detections) if detections else image
    cv2.imwrite(str(output_path), canvas)
    logger.info("Saved result to %s", output_path)


def create_comparison_grid(
    images: list[np.ndarray],
    titles: list[str] = None,
    cols: int = 4,
) -> np.ndarray:
    """Arrange images into a grid for comparison.

    Args:
        images: List of BGR images (must be same size or will be resized).
        titles: Optional titles for each image.
        cols: Number of columns in the grid.

    Returns:
        Grid image as numpy array.
    """
    if not images:
        return np.zeros((100, 100, 3), dtype=np.uint8)

    h, w = images[0].shape[:2]
    for i, img in enumerate(images):
        if img.shape[:2] != (h, w):
            images[i] = cv2.resize(img, (w, h))

    rows = (len(images) + cols - 1) // cols
    grid = np.zeros((h * rows, w * cols, 3), dtype=np.uint8)

    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        grid[r * h:(r + 1) * h, c * w:(c + 1) * w] = img
        if titles and i < len(titles):
            cv2.putText(grid, titles[i], (c * w + 5, r * h + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return grid
