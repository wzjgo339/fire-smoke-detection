export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectionResult {
  bbox: [number, number, number, number];
  class: "smoke" | "fire";
  class_id: 0 | 1;
  confidence: number;
}

export interface ImageDetectionResponse {
  id: string;
  filename: string;
  original_url: string;
  annotated_url: string | null;
  thumbnail_url: string | null;
  detections: DetectionResult[];
  total_count: number;
  smoke_count: number;
  fire_count: number;
  max_confidence: number | null;
  processing_time_ms: number | null;
  image_width: number | null;
  image_height: number | null;
}

export interface VideoTaskSubmitResponse {
  task_id: string;
  status: string;
  filename: string;
  total_frames: number | null;
  estimated_seconds: number | null;
  created_at: string | null;
}

export interface TimelinePoint {
  t: number;
  count: number;
}

export interface FrameDetection {
  frame_index: number;
  timestamp_sec: number | null;
  detections: DetectionResult[];
  count: number;
}

export interface VideoTaskStatusResponse {
  task_id: string;
  status: "processing" | "completed" | "failed";
  progress_pct: number | null;
  frames_processed: number | null;
  frames_total: number | null;
  current_fps: number | null;
  filename: string | null;
  annotated_url: string | null;
  original_url: string | null;
  duration_seconds: number | null;
  total_frames: number | null;
  total_detections: number | null;
  smoke_count: number | null;
  fire_count: number | null;
  processing_time_ms: number | null;
  results: FrameDetection[] | null;
  timeline: TimelinePoint[] | null;
  error: string | null;
  created_at: string | null;
}
