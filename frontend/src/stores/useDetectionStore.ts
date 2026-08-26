import { create } from "zustand";
import type { ImageDetectionResponse, VideoTaskStatusResponse } from "../types/detection";
import { detectImage, detectVideo, getVideoStatus } from "../services/detectionApi";

interface DetectionState {
  isProcessing: boolean;
  uploadProgress: number;
  error: string | null;

  currentImageResult: ImageDetectionResponse | null;
  currentVideoTask: VideoTaskStatusResponse | null;

  uploadAndDetectImage: (file: File, conf: number, iou: number) => Promise<void>;
  uploadVideo: (file: File, conf: number, iou: number, frameSkip: number) => Promise<string>;
  pollVideoStatus: (taskId: string) => Promise<boolean>;
  resetResults: () => void;
  clearError: () => void;
}

export const useDetectionStore = create<DetectionState>((set) => ({
  isProcessing: false,
  uploadProgress: 0,
  error: null,
  currentImageResult: null,
  currentVideoTask: null,

  uploadAndDetectImage: async (file, conf, iou) => {
    set({ isProcessing: true, uploadProgress: 0, error: null, currentImageResult: null });
    try {
      const result = await detectImage(file, conf, iou, (pct) => set({ uploadProgress: pct }));
      set({ currentImageResult: result, isProcessing: false });
    } catch (e) {
      set({ error: (e as Error).message, isProcessing: false });
    }
  },

  uploadVideo: async (file, conf, iou, frameSkip) => {
    set({ isProcessing: true, error: null, currentVideoTask: null });
    try {
      const result = await detectVideo(file, conf, iou, frameSkip);
      set({
        currentVideoTask: {
          task_id: result.task_id,
          status: "processing",
          progress_pct: 0,
          frames_processed: null,
          frames_total: result.total_frames,
          filename: result.filename,
          current_fps: null,
          annotated_url: null,
          original_url: null,
          duration_seconds: null,
          total_frames: result.total_frames,
          total_detections: null,
          smoke_count: null,
          fire_count: null,
          processing_time_ms: null,
          results: null,
          timeline: null,
          error: null,
          created_at: result.created_at,
        },
        isProcessing: false,
      });
      return result.task_id;
    } catch (e) {
      set({ error: (e as Error).message, isProcessing: false });
      return "";
    }
  },

  pollVideoStatus: async (taskId) => {
    try {
      const status = await getVideoStatus(taskId);
      set({ currentVideoTask: status });
      return status.status === "completed" || status.status === "failed";
    } catch (e) {
      set({ error: (e as Error).message });
      return true;
    }
  },

  resetResults: () => set({ currentImageResult: null, currentVideoTask: null, error: null }),
  clearError: () => set({ error: null }),
}));
