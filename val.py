"""Evaluation script for fire & smoke detection models."""

import argparse
import json
import logging
from pathlib import Path

from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Project root = this script's directory; keeps the project portable.
ROOT = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate fire & smoke detection model")
    parser.add_argument("--model", required=True, help="Path to model weights (.pt)")
    parser.add_argument("--data", default=str(ROOT / "data.yaml"), help="data.yaml path")
    parser.add_argument("--split", default="test", choices=["test", "val"], help="Which split to evaluate on")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.5, help="NMS IoU threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", default="0", help="Device")
    parser.add_argument("--save-json", action="store_true", help="Save metrics as JSON")
    parser.add_argument("--output", default=None, help="Output directory for plots")
    return parser.parse_args()


def main():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    logger.info("Loading model: %s", model_path)
    model = YOLO(str(model_path))

    # Guard: ensure class-name mapping is consistent with data.yaml (0=smoke, 1=fire).
    # Harmless no-op when the checkpoint already baked these names.
    model.model.names = {0: "smoke", 1: "fire"}

    data_path = args.data
    if args.split == "val":
        logger.info("Evaluating on validation set")
    else:
        logger.info("Evaluating on test set")

    metrics = model.val(
        data=data_path,
        split=args.split,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        device=args.device,
        plots=True,
    )

    logger.info("=== Evaluation Results ===")
    logger.info("mAP@50:       %.4f", metrics.box.map50)
    logger.info("mAP@50-95:    %.4f", metrics.box.map)
    logger.info("mAP@75:       %.4f", metrics.box.map75 if hasattr(metrics.box, "map75") else float("nan"))

    if hasattr(metrics.box, "ap_class_index") and metrics.box.ap is not None:
        for i, ap in zip(metrics.box.ap_class_index, metrics.box.ap):
            name = "smoke" if i == 0 else "fire"
            logger.info("  %s: mAP@50-95 = %.4f", name, ap)

    if hasattr(metrics.box, "mp"):
        logger.info("Precision:    %.4f", metrics.box.mp)
    if hasattr(metrics.box, "mr"):
        logger.info("Recall:       %.4f", metrics.box.mr)

    logger.info("Results saved to: %s", model.trainer.save_dir if model.trainer else "runs/detect/val")

    if args.save_json:
        results = {
            "model": str(model_path),
            "split": args.split,
            "conf": args.conf,
            "iou": args.iou,
            "map50": float(metrics.box.map50),
            "map50_95": float(metrics.box.map),
        }
        if hasattr(metrics.box, "mp"):
            results["precision"] = float(metrics.box.mp)
        if hasattr(metrics.box, "mr"):
            results["recall"] = float(metrics.box.mr)

        json_path = Path(args.output or ".") / "metrics.json"
        json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Metrics saved to: %s", json_path)


if __name__ == "__main__":
    main()
