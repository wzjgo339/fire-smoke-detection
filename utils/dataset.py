"""Dataset analysis utilities for D-Fire dataset."""

import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


def count_instances(labels_dir: Path) -> dict[str, int]:
    """Count total fire/smoke instances and empty labels in a labels directory."""
    stats = {"fire": 0, "smoke": 0, "empty": 0, "total_images": 0}
    for label_file in sorted(labels_dir.glob("*.txt")):
        stats["total_images"] += 1
        has_content = False
        try:
            with open(label_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    has_content = True
                    cls = line.split()[0]
                    if cls == "0":
                        stats["fire"] += 1
                    elif cls == "1":
                        stats["smoke"] += 1
        except Exception:
            logger.warning("Failed to read %s", label_file)
        if not has_content:
            stats["empty"] += 1
    return stats


def analyze_dataset(root: Path) -> dict:
    """Analyze full D-Fire dataset and return summary dict."""
    result = {}
    for split in ("train", "test"):
        labels_dir = root / split / "labels"
        if labels_dir.exists():
            stats = count_instances(labels_dir)
            stats["images"] = stats["total_images"]
            del stats["total_images"]
            result[split] = stats

    total = defaultdict(int)
    for s in result.values():
        for k, v in s.items():
            total[k] += v
    result["total"] = dict(total)
    return result
