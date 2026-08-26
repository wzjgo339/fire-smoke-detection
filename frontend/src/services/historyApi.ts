import api from "./api";
import type { HistoryDetail, PaginatedHistory } from "../types/history";

interface HistoryParams {
  page?: number;
  page_size?: number;
  type?: string;
  search?: string;
  has_detections?: boolean;
  sort_by?: string;
  sort_order?: string;
}

export async function fetchHistory(params: HistoryParams): Promise<PaginatedHistory> {
  const { data } = await api.get<PaginatedHistory>("/history", { params });
  return data;
}

export async function fetchHistoryDetail(id: string): Promise<HistoryDetail> {
  const { data } = await api.get<HistoryDetail>(`/history/${id}`);
  return data;
}

export async function deleteHistoryItem(id: string): Promise<void> {
  await api.delete(`/history/${id}`);
}
