import type { HistoryItem } from "./history";

export interface DashboardStats {
  total_records: number;
  total_images: number;
  total_videos: number;
  total_detections: number;
  total_fire: number;
  total_smoke: number;
  today_count: number;
  detections_by_day: { date: string; count: number }[];
  confidence_distribution: Record<string, number>;
  class_pie: { fire: number; smoke: number };
  avg_confidence_fire: number | null;
  avg_confidence_smoke: number | null;
  recent_activity: HistoryItem[];
}
