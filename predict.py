"""Inference script for fire & smoke detection.

Supports: single image, image directory, video file, and webcam input.
Outputs: visualized results with bounding boxes + JSON detection data.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from utils.visualization import draw_detections, save_result_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(r"E:\火灾识别")
CLASS_NAMES = {0: "smoke", 1: "fire"}


def parse_args():
    parser = argparse.ArgumentParser(description="Fire & smoke detection inference")
    parser.add_argument("--model", required=True, help="Path to model weights (.pt or .engine)")
    parser.add_argument("--source", required=True, help="Image path, directory, video path, or 'webcam'")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.5, help="NMS IoU threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--device", default="0", help="Device")
    parser.add_argument("--save", action="store_true", help="Save results to disk")
    parser.add_argument("--output", default="samples/output", help="Output directory")
    parser.add_argument("--show", action="store_true", help="Display results in window")
    parser.add_argument("--save-json", action="store_true", help="Save detection results as JSON")
    parser.add_argument("--nosave-img", action="store_true", help="Skip saving annotated images")
    parser.add_argument("--half", action="store_true", default=True, help="FP16 inference")
    return parser.parse_args()


def extract_detections(result, conf_threshold: float = 0.0) -> list[dict]:
    """Convert Ultralytics Results to structured detection dicts."""
    detections = []
    if result.boxes is None:
        return detections
    for box in result.boxes:
        conf = float(box.conf[0])
        if conf < conf_threshold:
            continue
        cls_id = int(box.cls[0])
        xyxy = box.xyxy[0].tolist()
        detections.append({
            "bbox": [round(x, 1) for x in xyxy],
            "class": CLASS_NAMES.get(cls_id, "unknown"),
            "class_id": cls_id,
            "confidence": round(conf, 4),
        })
    return detections


def process_image_directory(model, source_dir: Path, args):
    """Run inference on all images in a directory."""
    image_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    image_files = sorted(p for p in source_dir.iterdir() if p.suffix.lower() in image_exts)
    if not image_files:
        logger.error("No images found in %s", source_dir)
        return

    logger.info("Processing %d images from %s", len(image_files), source_dir)
    all_results = []
    out_dir = Path(args.output)

    for img_path in image_files:
        results = model(str(img_path), conf=args.conf, iou=args.iou, imgsz=args.imgsz,
                        device=args.device, half=args.half, verbose=False)
        for r in results:
            dets = extract_detections(r, args.conf)
            all_results.append({
                "image": str(img_path),
                "detections": dets,
                "count": len(dets),
            })
            logger.info("  %s: %d detections", img_path.name, len(dets))

            if not args.nosave_img:
                img = cv2.imread(str(img_path))
                if img is not None:
                    annotated = draw_detections(img, dets)
                    save_result_image(annotated, out_dir / img_path.name, dets)

    if args.save_json:
        json_path = out_dir / "detections.json"
        json_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("JSON results saved to %s", json_path)

    logger.info("Done. Processed %d images.", len(image_files))


def process_video(model, source: str, args):
    """Run inference on a video file."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.error("Cannot open video: %s", source)
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info("Video: %dx%d @ %.1f fps, %d frames", width, height, fps, total_frames)

    out_path = Path(args.output) / f"pred_{Path(source).name}" if args.save else None
    writer = None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        results = model(frame, conf=args.conf, iou=args.iou, imgsz=args.imgsz,
                        device=args.device, half=args.half, verbose=False)
        dets = extract_detections(results[0], args.conf)

        if args.show or args.save:
            annotated = draw_detections(frame, dets)
            if args.show:
                cv2.imshow("Fire & Smoke Detection", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            if writer:
                writer.write(annotated)

        if frame_idx % 100 == 0:
            logger.info("  Frame %d/%d", frame_idx, total_frames)

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    logger.info("Video processing done. %d frames.", frame_idx)


def process_webcam(model, args):
    """Run real-time inference on webcam feed."""
    cam_id = 0 if args.source == "webcam" else int(args.source)
    cap = cv2.VideoCapture(cam_id)
    if not cap.isOpened():
        logger.error("Cannot open webcam (id=%d)", cam_id)
        return

    logger.info("Webcam started. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=args.conf, iou=args.iou, imgsz=args.imgsz,
                        device=args.device, half=args.half, verbose=False)
        dets = extract_detections(results[0], args.conf)
        annotated = draw_detections(frame, dets)

        cv2.imshow("Fire & Smoke Detection (webcam)", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    args = parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        logger.error("Model not found: %s", model_path)
        sys.exit(1)

    logger.info("Loading model: %s", model_path)
    model = YOLO(str(model_path))

    source = args.source
    source_path = Path(source) if source != "webcam" and not source.isdigit() else None

    if source == "webcam" or (source.isdigit() and 0 <= int(source) <= 99):
        process_webcam(model, args)
    elif source_path and source_path.is_dir():
        process_image_directory(model, source_path, args)
    elif source_path and source_path.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
        process_video(model, source, args)
    elif source_path and source_path.is_file():
        # Single image
        results = model(source, conf=args.conf, iou=args.iou, imgsz=args.imgsz,
                        device=args.device, half=args.half, verbose=False)
        dets = extract_detections(results[0], args.conf)
        logger.info("Detections: %d", len(dets))
        for d in dets:
            logger.info("  %s: %.4f @ %s", d["class"], d["confidence"], d["bbox"])

        if not args.nosave_img:
            img = cv2.imread(source)
            if img is not None:
                out_path = Path(args.output) / Path(source).name
                save_result_image(img, out_path, dets)

        if args.save_json:
            json_path = Path(args.output) / "detections.json"
            json_path.write_text(json.dumps([{
                "image": source,
                "detections": dets,
                "count": len(dets),
            }], indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info("JSON saved to %s", json_path)
    else:
        logger.error("Source not found or unsupported: %s", source)
        sys.exit(1)


if __name__ == "__main__":
    main()
