import cv2
import numpy as np

color_map = {
    "fire": (0, 0, 255),
    "smoke": (0, 165, 255),
}


def draw_detections(
    image: np.ndarray,
    detections: list[dict],
    conf_threshold: float = 0.0,
    line_width: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
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
