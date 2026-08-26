import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.router import api_router
from .config import settings
from .database import init_db
from .services.file_service import cleanup_old_files

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "images").mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "videos").mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "_tmp").mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "results" / "images").mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "results" / "thumbs").mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "results" / "videos").mkdir(parents=True, exist_ok=True)
    logger.info("Upload directories created")
    # Remove uploads older than the retention window (default 30 days).
    try:
        await asyncio.to_thread(cleanup_old_files)
        logger.info("Old upload cleanup completed")
    except Exception as e:
        logger.warning("Cleanup of old uploads failed: %s", e)
    yield


app = FastAPI(
    title="Fire & Smoke Detection API",
    description="Detect fire and smoke in images, videos, and live webcam streams using YOLOv8m + TensorRT.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# In production, serve frontend static files
frontend_dist = settings.PROJECT_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    logger.info("Serving frontend from %s", frontend_dist)
    # Mount frontend assets
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA — return index.html for all non-API, non-upload paths."""
        path = frontend_dist / full_path
        if path.exists() and path.is_file():
            return FileResponse(str(path))
        return FileResponse(str(frontend_dist / "index.html"))
