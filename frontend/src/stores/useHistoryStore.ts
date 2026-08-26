import { create } from "zustand";
import type { HistoryItem } from "../types/history";
import { fetchHistory, deleteHistoryItem } from "../services/historyApi";

interface HistoryState {
  items: HistoryItem[];
  total: number;
  page: number;
  pageSize: number;
  filters: { type?: string; search?: string; has_detections?: boolean };
  isLoading: boolean;
  error: string | null;

  loadHistory: () => Promise<void>;
  setPage: (page: number) => void;
  setFilters: (filters: Partial<HistoryState["filters"]>) => void;
  deleteItem: (id: string) => Promise<void>;
}

export const useHistoryStore = create<HistoryState>((set, get) => ({
  items: [],
  total: 0,
  page: 1,
  pageSize: 20,
  filters: {},
  isLoading: false,
  error: null,

  loadHistory: async () => {
    const { page, pageSize, filters } = get();
    set({ isLoading: true, error: null });
    try {
      const params: Record<string, string | number | boolean> = { page, page_size: pageSize };
      if (filters.type) params.type = filters.type;
      if (filters.search) params.search = filters.search;
      if (filters.has_detections !== undefined) params.has_detections = filters.has_detections;
      const result = await fetchHistory(params as never);
      set({ items: result.items, total: result.total, isLoading: false });
    } catch (e) {
      set({ error: (e as Error).message, isLoading: false });
    }
  },

  setPage: (page) => {
    set({ page });
    get().loadHistory();
  },

  setFilters: (filters) => {
    set({ filters: { ...get().filters, ...filters }, page: 1 });
    get().loadHistory();
  },

  deleteItem: async (id) => {
    try {
      await deleteHistoryItem(id);
      get().loadHistory();
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },
}));
