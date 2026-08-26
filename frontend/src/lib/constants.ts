export const API_BASE = "/api";
export const DEFAULT_CONFIDENCE = 0.25;
export const DEFAULT_IOU = 0.5;
export const MAX_IMAGE_SIZE = 20 * 1024 * 1024; // 20 MB
export const MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024; // 2 GB
export const VIDEO_POLL_INTERVAL = 2000; // 2s

export const CLASS_COLORS: Record<string, string> = {
  fire: "#EF4444",
  smoke: "#F97316",
};
