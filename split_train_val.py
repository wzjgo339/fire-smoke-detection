"""Stratified train/val split for D-Fire dataset.

Splits the official train set 90/10, preserving class distribution across splits.
Groups images by label composition (fire-only, smoke-only, both, empty) and
samples each group independently.
"""

import logging
import random
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(r"E:\火灾识别")
TRAIN_IMAGES = ROOT / "train" / "images"
TRAIN_LABELS = ROOT / "train" / "labels"
OUTPUT_DIR = ROOT / "data"
VAL_RATIO = 0.1
SEED = 42


def classify_image(label_path: Path) -> str:
    """Return composition label for an image: fire_only, smoke_only, both, empty."""
    has_fire = False
    has_smoke = False
    try:
        with open(label_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cls = line.split()[0]
                if cls == "0":
                    has_fire = True
                elif cls == "1":
                    has_smoke = True
    except Exception:
        logger.warning("Failed to read %s", label_path)
        return "empty"
    if has_fire and has_smoke:
        return "both"
    if has_fire:
        return "fire_only"
    if has_smoke:
        return "smoke_only"
    return "empty"


def main():
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    groups: dict[str, list[str]] = defaultdict(list)
    for img_path in sorted(TRAIN_IMAGES.glob("*.jpg")):
        label_path = TRAIN_LABELS / (img_path.stem + ".txt")
        if label_path.exists():
            group = classify_image(label_path)
        else:
            group = "empty"
        groups[group].append(str(img_path.resolve()))

    train_paths: list[str] = []
    val_paths: list[str] = []

    for group_name, paths in groups.items():
        random.shuffle(paths)
        n_val = max(1, int(len(paths) * VAL_RATIO))
        val_paths.extend(paths[:n_val])
        train_paths.extend(paths[n_val:])
        logger.info(
            "%s: %d total -> %d train / %d val",
            group_name, len(paths), len(paths) - n_val, n_val,
        )

    random.shuffle(train_paths)
    random.shuffle(val_paths)

    train_txt = OUTPUT_DIR / "train.txt"
    val_txt = OUTPUT_DIR / "val.txt"
    train_txt.write_text("\n".join(train_paths), encoding="utf-8")
    val_txt.write_text("\n".join(val_paths), encoding="utf-8")

    logger.info("Wrote %d train paths -> %s", len(train_paths), train_txt)
    logger.info("Wrote %d val paths   -> %s", len(val_paths), val_txt)


if __name__ == "__main__":
    main()
