import api from "./api";
import type { ImageDetectionResponse, VideoTaskSubmitResponse, VideoTaskStatusResponse } from "../types/detection";

export async function detectImage(
  file: File,
  confidence: number,
  iou: number,
  onProgress?: (pct: number) => void
): Promise<ImageDetectionResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("confidence", String(confidence));
  form.append("iou", String(iou));
  const { data } = await api.post<ImageDetectionResponse>("/detect/image", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return data;
}

export async function detectVideo(
  file: File,
  confidence: number,
  iou: number,
  frameSkip: number
): Promise<VideoTaskSubmitResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("confidence", String(confidence));
  form.append("iou", String(iou));
  form.append("frame_skip", String(frameSkip));
  const { data } = await api.post<VideoTaskSubmitResponse>("/detect/video", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getVideoStatus(taskId: string): Promise<VideoTaskStatusResponse> {
  const { data } = await api.get<VideoTaskStatusResponse>(`/detect/video/${taskId}`);
  return data;
}
