import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { EmptyState } from "../common/EmptyState";

interface Props {
  data: Record<string, number>;
  title: string;
}

/** Charts the distribution of detection confidence across buckets of 0.1. */
export function ConfidenceDistributionChart({ data, title }: Props) {
  const entries = Object.entries(data || {})
    .map(([range, count]) => ({ range, count }))
    .sort((a, b) => parseFloat(a.range) - parseFloat(b.range));
  const hasData = entries.length > 0;

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">检测框置信度分桶（置信度区间 → 数量）</p>
      </div>
      {!hasData ? (
        <EmptyState title="暂无置信度数据" className="py-12" />
      ) : (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={entries} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <XAxis
                dataKey="range"
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
                formatter={(value) => [`${value}`, "检测数"]}
                labelStyle={{ color: "#94a3b8", fontSize: 12 }}
                contentStyle={{
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="count" fill="#f97316" radius={[4, 4, 0, 0]} maxBarSize={42} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
