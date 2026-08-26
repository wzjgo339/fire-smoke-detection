import logging

logger = logging.getLogger(__name__)


def get_gpu_info() -> dict:
    """Get GPU memory and utilization via pynvml. Returns empty dict if GPU unavailable."""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        name = pynvml.nvmlDeviceGetName(handle).decode() if isinstance(pynvml.nvmlDeviceGetName(handle), bytes) else pynvml.nvmlDeviceGetName(handle)
        return {
            "name": name,
            "memory_total_mb": info.total // (1024 * 1024),
            "memory_used_mb": info.used // (1024 * 1024),
            "memory_free_mb": info.free // (1024 * 1024),
            "utilization_pct": pynvml.nvmlDeviceGetUtilizationRates(handle).gpu,
        }
    except Exception as e:
        logger.warning("Failed to get GPU info: %s", e)
        return {}
