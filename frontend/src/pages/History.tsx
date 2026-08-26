import { useEffect, useState } from "react";
import { Search, Trash2, Image, Video, ChevronLeft, ChevronRight, X } from "lucide-react";
import { PageHeader } from "../components/common/PageHeader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { EmptyState } from "../components/common/EmptyState";
import { CardSkeleton } from "../components/common/LoadingSkeleton";
import { useHistoryStore } from "../stores/useHistoryStore";
import { formatTimeAgo } from "../lib/utils";

export default function History() {
  const { items, total, page, pageSize, isLoading, error, loadHistory, setPage, setFilters, filters, deleteItem } =
    useHistoryStore();
  const [searchInput, setSearchInput] = useState("");

  useEffect(() => { loadHistory(); }, [loadHistory]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader title="检测历史" description="浏览和管理过去的检测记录" />

      {error && <ErrorAlert message={error} onDismiss={() => {}} />}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <div className="relative flex-1 max-w-xs">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text" placeholder="搜索文件名..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") setFilters({ search: searchInput || undefined });
            }}
            className="w-full pl-8 pr-3 py-2 text-sm border rounded-lg dark:bg-gray-900 dark:border-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <select
          value={filters.type || ""}
          onChange={(e) => setFilters({ type: e.target.value || undefined })}
          className="px-3 py-2 text-sm border rounded-lg dark:bg-gray-900 dark:border-gray-700 dark:text-gray-200"
        >
          <option value="">全部类型</option>
          <option value="image">图像</option>
          <option value="video">视频</option>
        </select>
        <select
          value={filters.has_detections === undefined ? "" : String(filters.has_detections)}
          onChange={(e) => {
            const v = e.target.value;
            setFilters({ has_detections: v === "" ? undefined : v === "true" });
          }}
          className="px-3 py-2 text-sm border rounded-lg dark:bg-gray-900 dark:border-gray-700 dark:text-gray-200"
        >
          <option value="">全部结果</option>
          <option value="true">有检测</option>
          <option value="false">无检测</option>
        </select>
        {(filters.type || filters.search || filters.has_detections !== undefined) && (
          <button
            onClick={() => {
              setSearchInput("");
              setFilters({ type: undefined, search: undefined, has_detections: undefined });
            }}
            className="flex items-center gap-1 px-2 py-2 text-xs text-gray-500 hover:text-gray-700"
          >
            <X className="w-3 h-3" /> 清除筛选
          </button>
        )}
      </div>

      {/* Content */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {!isLoading && items.length === 0 && !error && (
        <EmptyState title="暂无检测记录" description="上传图片或视频开始检测" />
      )}

      {!isLoading && items.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((item) => (
              <div
                key={item.id}
                className="group rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-md transition-all"
              >
                <div className="aspect-video bg-gray-100 dark:bg-gray-900 flex items-center justify-center overflow-hidden">
                  {item.thumbnail_url ? (
                    <img src={item.thumbnail_url} alt={item.filename} className="w-full h-full object-cover" />
                  ) : (
                    item.type === "image" ? <Image className="w-8 h-8 text-gray-400" /> : <Video className="w-8 h-8 text-gray-400" />
                  )}
                </div>
                <div className="p-3 space-y-1.5">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate" title={item.filename}>
                    {item.filename}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-500 uppercase">
                      {item.type}
                    </span>
                    {item.total_detections > 0 && (
                      <>
                        {item.fire_count > 0 && (
                          <span className="text-[10px] text-red-500">{item.fire_count} fire</span>
                        )}
                        {item.smoke_count > 0 && (
                          <span className="text-[10px] text-orange-500">{item.smoke_count} smoke</span>
                        )}
                      </>
                    )}
                    {item.total_detections === 0 && (
                      <span className="text-[10px] text-gray-400">无检测</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-400">{formatTimeAgo(item.created_at)}</span>
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/30 text-gray-400 hover:text-red-500 transition-all"
                      title="删除"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-800">
            <span className="text-xs text-gray-500">共 {total} 条记录</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-gray-600 dark:text-gray-400 px-3">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
                className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
