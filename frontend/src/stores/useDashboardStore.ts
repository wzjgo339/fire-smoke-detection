import { create } from "zustand";
import type { DashboardStats } from "../types/stats";
import { fetchStats } from "../services/statsApi";

interface DashboardState {
  stats: DashboardStats | null;
  isLoading: boolean;
  error: string | null;
  loadStats: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  isLoading: false,
  error: null,
  loadStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const stats = await fetchStats();
      set({ stats, isLoading: false });
    } catch (e) {
      set({ error: (e as Error).message, isLoading: false });
    }
  },
}));
