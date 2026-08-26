"""Export trained YOLO model to ONNX and TensorRT formats with benchmarking."""

import argparse
import logging
import time
from pathlib import Path

import numpy as np
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Export YOLO model for deployment")
    parser.add_argument("--model", required=True, help="Path to trained model (.pt)")
    parser.add_argument("--format", default="onnx", choices=["onnx", "engine", "tflite", "openvino", "all"],
                        help="Export format")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--half", action=argparse.BooleanOptionalAction, default=True,
                        help="FP16 precision (default on; use --no-half for FP32)")
    parser.add_argument("--dynamic", action="store_true", help="Dynamic batch size (ONNX/TensorRT)")
    parser.add_argument("--workspace", type=int, default=8, help="TensorRT workspace GB")
    parser.add_argument("--simplify", action="store_true", default=True, help="Simplify ONNX model")
    parser.add_argument("--benchmark", action="store_true", help="Run speed benchmark after export")
    parser.add_argument("--output", default=None, help="Output directory")
    return parser.parse_args()


def export_onnx(model: YOLO, args) -> Path:
    logger.info("Exporting ONNX (FP%d, opset=17, simplify=%s, dynamic=%s)...",
                16 if args.half else 32, args.simplify, args.dynamic)
    path = model.export(
        format="onnx",
        imgsz=args.imgsz,
        half=args.half,
        dynamic=args.dynamic,
        simplify=args.simplify,
        opset=17,
    )
    out = Path(path)
    size_mb = out.stat().st_size / (1024 * 1024)
    logger.info("ONNX model saved: %s (%.1f MB)", out, size_mb)
    return out


def export_tensorrt(model: YOLO, args) -> Path:
    logger.info("Exporting TensorRT (FP%d, dynamic=%s, workspace=%dGB)...",
                16 if args.half else 32, args.dynamic, args.workspace)
    path = model.export(
        format="engine",
        imgsz=args.imgsz,
        half=args.half,
        dynamic=args.dynamic,
        workspace=args.workspace,
    )
    out = Path(path)
    size_mb = out.stat().st_size / (1024 * 1024)
    logger.info("TensorRT engine saved: %s (%.1f MB)", out, size_mb)
    return out


def run_benchmark(model: YOLO, imgsz: int, num_warmup: int = 10, num_runs: int = 100):
    """Benchmark inference speed."""
    logger.info("Running benchmark (%d warmup + %d runs @ imgsz=%d)...",
                num_warmup, num_runs, imgsz)
    dummy = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype=np.uint8)

    # Warmup
    for _ in range(num_warmup):
        model(dummy, imgsz=imgsz, verbose=False)

    # Timed runs
    times = []
    for _ in range(num_runs):
        t0 = time.perf_counter()
        model(dummy, imgsz=imgsz, verbose=False)
        times.append(time.perf_counter() - t0)

    times = np.array(times) * 1000  # ms
    logger.info("Benchmark results (%d runs @ %dx%d):", num_runs, imgsz, imgsz)
    logger.info("  Mean:    %.1f ms", times.mean())
    logger.info("  Median:  %.1f ms", np.median(times))
    logger.info("  Min:     %.1f ms", times.min())
    logger.info("  Max:     %.1f ms", times.max())
    logger.info("  FPS:     %.1f", 1000 / times.mean())
    logger.info("  P95:     %.1f ms", np.percentile(times, 95))
    logger.info("  P99:     %.1f ms", np.percentile(times, 99))


def main():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    logger.info("Loading model: %s", model_path)
    model = YOLO(str(model_path))

    formats = ["onnx", "engine"] if args.format == "all" else [args.format]

    for fmt in formats:
        if fmt == "onnx":
            export_onnx(model, args)
        elif fmt == "engine":
            export_tensorrt(model, args)
        else:
            model.export(format=fmt, imgsz=args.imgsz, half=args.half)

    if args.benchmark:
        run_benchmark(model, args.imgsz)


if __name__ == "__main__":
    main()
