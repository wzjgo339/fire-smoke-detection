from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from ultralytics import YOLO

from ..config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Singleton managing YOLO model lifecycle and GPU inference serialization."""

    _instance: "ModelManager | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._model: YOLO | None = None
        self._model_loaded = False
        self._backend = "unknown"
        self._inference_lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._load_model()

    def _load_model(self):
        engine = settings.MODEL_PATH
        fallback = settings.MODEL_FALLBACK

        if engine.exists() and engine.suffix == ".engine":
            try:
                logger.info("Loading TensorRT engine: %s", engine)
                self._model = YOLO(str(engine), task="detect")
                self._backend = "tensorrt"
                self._model_loaded = True
                logger.info("TensorRT engine loaded successfully")
            except Exception as e:
                logger.warning("TensorRT load failed (%s), falling back to PyTorch", e)
        if not self._model_loaded:
            for pt_path in [fallback, engine]:
                if pt_path.exists() and pt_path.suffix == ".pt":
                    try:
                        logger.info("Loading PyTorch model: %s", pt_path)
                        self._model = YOLO(str(pt_path), task="detect")
                        self._backend = "pytorch"
                        self._model_loaded = True
                        break
                    except Exception as e:
                        logger.warning("PyTorch load failed for %s: %s", pt_path, e)

        if self._model_loaded and self._model is not None:
            try:
                # Guard: keep class-name mapping consistent with data.yaml (0=smoke, 1=fire).
                self._model.model.names = {0: "smoke", 1: "fire"}
            except Exception:
                logger.warning("Could not set model.names, using engine-baked names")

    @property
    def is_loaded(self) -> bool:
        return self._model_loaded

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def model_info(self) -> dict:
        return {
            "loaded": self._model_loaded,
            "path": str(settings.MODEL_PATH),
            "backend": self._backend,
            "input_size": [settings.MODEL_IMGSZ, settings.MODEL_IMGSZ],
            "classes": ["smoke", "fire"],
        }

    async def detect(self, image: np.ndarray, conf: float = 0.25, iou: float = 0.5) -> list:
        """Run detection on an image. Thread-safe via asyncio.Lock + executor."""
        if not self._model_loaded:
            raise RuntimeError("Model not loaded")

        async with self._inference_lock:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, self._inference_sync, image, conf, iou)

    def _inference_sync(self, image: np.ndarray, conf: float, iou: float) -> list:
        result = self._model(image, conf=conf, iou=iou, imgsz=settings.MODEL_IMGSZ, verbose=False)[0]
        dets = []
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()
            for bbox, cls_id, conf_val in zip(boxes, classes, confs):
                dets.append({
                    "bbox": [float(x) for x in bbox],
                    "class": "smoke" if cls_id == 0 else "fire",
                    "class_id": int(cls_id),
                    "confidence": float(conf_val),
                })
        return dets
