export interface HealthResponse {
  status: string;
  model: {
    loaded: boolean;
    path: string;
    backend: string;
    input_size: [number, number];
    classes: string[];
  };
  gpu: {
    name: string;
    memory_total_mb: number;
    memory_used_mb: number;
    memory_free_mb: number;
    utilization_pct: number;
  };
  uptime_seconds: number;
  queue_size: number;
}
