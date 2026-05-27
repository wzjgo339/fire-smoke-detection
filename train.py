"""Training script for fire & smoke detection using YOLOv8."""

import argparse
import logging
from datetime import datetime
from pathlib import Path

import yaml
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(r"E:\火灾识别")


def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for fire & smoke detection")
    parser.add_argument("--model", default="yolov8m.pt", help="Model weights or architecture")
    parser.add_argument("--config", default="configs/train_yolov8m.yaml", help="Training config YAML")
    parser.add_argument("--epochs", type=int, default=None, help="Override epochs")
    parser.add_argument("--batch", type=int, default=None, help="Override batch size")
    parser.add_argument("--imgsz", type=int, default=None, help="Override image size")
    parser.add_argument("--device", default="0", help="Device: 0, cpu, or 0,1 for multi-GPU")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--name", default=None, help="Experiment name (auto-generated if omitted)")
    parser.add_argument("--workers", type=int, default=None, help="DataLoader workers (read from config if omitted)")
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def build_train_kwargs(cfg: dict, args) -> dict:
    kwargs = {
        "data": str(ROOT / "data.yaml"),
        "epochs": args.epochs or cfg.get("epochs", 200),
        "batch": args.batch or cfg.get("batch", 32),
        "imgsz": args.imgsz or cfg.get("imgsz", 640),
        "device": args.device,
        "workers": args.workers or cfg.get("workers", 8),
        "seed": cfg.get("seed", 42),
        "optimizer": cfg.get("optimizer", "SGD"),
        "lr0": cfg.get("lr0", 0.01),
        "lrf": cfg.get("lrf", 0.01),
        "momentum": cfg.get("momentum", 0.937),
        "weight_decay": cfg.get("weight_decay", 0.0005),
        "warmup_epochs": cfg.get("warmup_epochs", 3.0),
        "warmup_momentum": cfg.get("warmup_momentum", 0.8),
        "warmup_bias_lr": cfg.get("warmup_bias_lr", 0.1),
        "patience": cfg.get("patience", 30),
        "close_mosaic": cfg.get("close_mosaic", 10),
        "box": cfg.get("box", 7.5),
        "cls": cfg.get("cls", 0.5),
        "dfl": cfg.get("dfl", 1.5),
        "hsv_h": cfg.get("hsv_h", 0.015),
        "hsv_s": cfg.get("hsv_s", 0.7),
        "hsv_v": cfg.get("hsv_v", 0.4),
        "translate": cfg.get("translate", 0.1),
        "scale": cfg.get("scale", 0.5),
        "fliplr": cfg.get("fliplr", 0.5),
        "mosaic": cfg.get("mosaic", 1.0),
        "amp": cfg.get("amp", True),
        "cache": cfg.get("cache", False),
        "resume": args.resume,
        "project": "runs/detect",
    }
    if args.name:
        kwargs["name"] = args.name
    else:
        arch = Path(args.model).stem
        kwargs["name"] = f"fire_smoke_{arch}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    return kwargs


def main():
    args = parse_args()
    cfg = load_config(args.config)
    kwargs = build_train_kwargs(cfg, args)

    logger.info("Training %s | epochs=%d | batch=%d | imgsz=%d | name=%s",
                args.model, kwargs["epochs"], kwargs["batch"], kwargs["imgsz"], kwargs["name"])
    logger.info("Optimizer: %s | lr=%.4f | momentum=%.3f | weight_decay=%.5f",
                kwargs["optimizer"], kwargs["lr0"], kwargs["momentum"], kwargs["weight_decay"])
    logger.info("Data: %s", kwargs["data"])
    logger.info("AMP: %s | Mosaic close: epoch %d | Warmup: %.1f epochs",
                kwargs["amp"], kwargs["close_mosaic"], kwargs["warmup_epochs"])

    model = YOLO(args.model)
    results = model.train(**kwargs)

    best_pt = Path(model.trainer.save_dir) / "weights" / "best.pt"
    if best_pt.exists():
        logger.info("Best model saved to: %s", best_pt)

    return results


if __name__ == "__main__":
    main()
