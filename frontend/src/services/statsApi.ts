import type { DashboardStats } from "../types/stats";
import api from "./api";

export async function fetchStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/stats");
  return data;
}
