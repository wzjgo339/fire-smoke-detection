import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { EmptyState } from "../common/EmptyState";

interface DayPoint {
  date: string;
  count: number;
}

interface Props {
  data: DayPoint[];
  title: string;
  description?: string;
}

/** Charts daily detection counts over a rolling window (detections_by_day). */
export function DetectionTrendChart({ data, title, description }: Props) {
  const showEmpty = !data || data.length === 0;

  // Keep X-axis labels compact ("MM-DD").
  const chartData = data.map((p) => ({
    ...p,
    label: p.date.length > 10 ? p.date.slice(5, 10) : p.date,
  }));

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
        {description && <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{description}</p>}
      </div>
      {showEmpty ? (
        <EmptyState title="暂无趋势数据" description="上传图片或视频产生检测后，这里会显示每日趋势" className="py-12" />
      ) : (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "rgba(148,163,184,0.08)" }}
                formatter={(value) => [`${value}`, "检测次数"]}
                labelStyle={{ color: "#94a3b8", fontSize: 12 }}
                contentStyle={{
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={42} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
