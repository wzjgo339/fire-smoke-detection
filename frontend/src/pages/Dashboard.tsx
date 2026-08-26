import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Image, Video, Camera, Flame, FlameIcon, AlertTriangle, ArrowRight, TrendingUp, Gauge } from "lucide-react";
import { PageHeader } from "../components/common/PageHeader";
import { StatsCard } from "../components/common/StatsCard";
import { CardSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { EmptyState } from "../components/common/EmptyState";
import { DetectionTrendChart } from "../components/detection/DetectionTrendChart";
import { ConfidenceDistributionChart } from "../components/detection/ConfidenceDistributionChart";
import { useDashboardStore } from "../stores/useDashboardStore";
import { formatTimeAgo } from "../lib/utils";
import { CLASS_COLORS } from "../lib/constants";

export default function Dashboard() {
  const { stats, isLoading, error, loadStats } = useDashboardStore();

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="仪表盘"
        description="火灾与烟雾检测系统概览"
      />

      {error && <ErrorAlert message={error} onRetry={loadStats} onDismiss={() => {}} />}

      {isLoading && !stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {stats && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatsCard
              label="总检测次数"
              value={stats.total_detections}
              icon={<AlertTriangle className="w-5 h-5" />}
              accent="primary"
            />
            <StatsCard
              label="火灾检测"
              value={stats.total_fire}
              icon={<Flame className="w-5 h-5" />}
              accent="fire"
            />
            <StatsCard
              label="烟雾检测"
              value={stats.total_smoke}
              icon={<FlameIcon className="w-5 h-5" />}
              accent="smoke"
            />
            <StatsCard
              label="今日"
              value={stats.today_count}
              icon={<Camera className="w-5 h-5" />}
              accent="default"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Class distribution */}
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">类别分布</h3>
              {stats.total_fire + stats.total_smoke === 0 ? (
                <EmptyState title="暂无数据" />
              ) : (
                <div className="flex items-center gap-6">
                  <div className="flex-1 space-y-3">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span style={{ color: CLASS_COLORS.fire }}>Fire</span>
                        <span className="text-gray-500">{stats.total_fire}</span>
                      </div>
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div className="h-full bg-fire rounded-full" style={{
                          width: `${stats.total_fire + stats.total_smoke > 0 ? (stats.total_fire / (stats.total_fire + stats.total_smoke) * 100).toFixed(0) : 0}%`
                        }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span style={{ color: CLASS_COLORS.smoke }}>Smoke</span>
                        <span className="text-gray-500">{stats.total_smoke}</span>
                      </div>
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div className="h-full bg-smoke rounded-full" style={{
                          width: `${stats.total_fire + stats.total_smoke > 0 ? (stats.total_smoke / (stats.total_fire + stats.total_smoke) * 100).toFixed(0) : 0}%`
                        }} />
                      </div>
                    </div>
                  </div>
                  {/* Pie chart (simple CSS) */}
                  <div className="w-20 h-20 rounded-full border-4 border-fire dark:border-fire/70"
                    style={{
                      background: `conic-gradient(#EF4444 0deg ${stats.total_fire / Math.max(stats.total_fire + stats.total_smoke, 1) * 360}deg, #F97316 ${stats.total_fire / Math.max(stats.total_fire + stats.total_smoke, 1) * 360}deg 360deg)`
                    }}
                  />
                </div>
              )}
            </div>

            {/* Quick stats */}
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">记录概览</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-900">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_images}</div>
                  <div className="text-xs text-gray-500">图像检测</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-900">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_videos}</div>
                  <div className="text-xs text-gray-500">视频检测</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-900 col-span-2">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_records}</div>
                  <div className="text-xs text-gray-500">总记录数</div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts: detection trend + confidence distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <DetectionTrendChart
              data={stats.detections_by_day}
              title="近 14 天检测趋势"
              description="每天新增的检测记录数"
            />
            <ConfidenceDistributionChart
              data={stats.confidence_distribution}
              title="置信度分布"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-red-50 dark:bg-red-950/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1.5">火检平均置信度 <Gauge className="w-3.5 h-3.5" /></p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.avg_confidence_fire !== null && stats.avg_confidence_fire !== undefined
                    ? (stats.avg_confidence_fire * 100).toFixed(1) + "%"
                    : "-"}
                </p>
              </div>
            </div>
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-orange-50 dark:bg-orange-950/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1.5">烟检平均置信度 <Gauge className="w-3.5 h-3.5" /></p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.avg_confidence_smoke !== null && stats.avg_confidence_smoke !== undefined
                    ? (stats.avg_confidence_smoke * 100).toFixed(1) + "%"
                    : "-"}
                </p>
              </div>
            </div>
          </div>

          {/* Recent activity */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">最近活动</h3>
              <Link to="/history" className="text-xs text-blue-500 hover:underline flex items-center gap-1">
                查看全部 <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            {stats.recent_activity.length === 0 ? (
              <EmptyState title="暂无活动" description="上传图片或视频开始检测" />
            ) : (
              <div className="space-y-2">
                {stats.recent_activity.map((item) => (
                  <div key={item.id} className="flex items-center gap-3 py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                    {item.thumbnail_url ? (
                      <img src={item.thumbnail_url} alt="" className="w-10 h-10 rounded object-cover" />
                    ) : (
                      <div className="w-10 h-10 rounded bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        {item.type === "image" ? <Image className="w-4 h-4 text-gray-400" /> : <Video className="w-4 h-4 text-gray-400" />}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700 dark:text-gray-300 truncate">{item.filename}</p>
                      <p className="text-xs text-gray-500">
                        {item.total_detections} 个检测 · {formatTimeAgo(item.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
