export interface HistoryItem {
  id: string;
  type: "image" | "video";
  filename: string;
  thumbnail_url: string | null;
  total_detections: number;
  smoke_count: number;
  fire_count: number;
  max_confidence: number | null;
  processing_time_ms: number | null;
  created_at: string | null;
}

export interface HistoryDetail extends HistoryItem {
  original_url: string | null;
  annotated_url: string | null;
  image_width: number | null;
  image_height: number | null;
  detections: Record<string, unknown>[];
}

export interface PaginatedHistory {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
