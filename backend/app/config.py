from pathlib import Path

from pydantic_settings import BaseSettings

# Project root derived from this file's location (backend/app/config.py) so the
# project is portable across machines instead of being hard-wired to a drive path.
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    PROJECT_ROOT: Path = ROOT
    MODEL_PATH: Path = ROOT / "runs/detect/fire_smoke_yolov8m_20260526_2202/weights/best.engine"
    MODEL_FALLBACK: Path = ROOT / "runs/detect/fire_smoke_yolov8m_20260526_2202/weights/best.pt"
    MODEL_CONF_DEFAULT: float = 0.25
    MODEL_IOU_DEFAULT: float = 0.5
    MODEL_IMGSZ: int = 640

    UPLOAD_DIR: Path = ROOT / "backend/uploads"
    MAX_IMAGE_SIZE: int = 20 * 1024 * 1024
    MAX_VIDEO_SIZE: int = 2 * 1024 * 1024 * 1024

    DATABASE_URL: str = f"sqlite+aiosqlite:///{ROOT.as_posix()}/backend/db/fire_detection.db"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    DEFAULT_FRAME_SKIP: int = 1
    MAX_VIDEO_FRAMES: int = 0
    CLEANUP_DAYS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
