import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

interface Props {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: string;
  trendUp?: boolean;
  accent?: "default" | "fire" | "smoke" | "primary";
}

const accentStyles: Record<string, string> = {
  default: "border-gray-200 dark:border-gray-800",
  fire: "border-red-500/30 dark:border-red-500/20 bg-red-50/50 dark:bg-red-950/20",
  smoke: "border-orange-500/30 dark:border-orange-500/20 bg-orange-50/50 dark:bg-orange-950/20",
  primary: "border-blue-500/30 dark:border-blue-500/20 bg-blue-50/50 dark:bg-blue-950/20",
};

const iconAccentStyles: Record<string, string> = {
  default: "text-gray-500",
  fire: "text-red-500",
  smoke: "text-orange-500",
  primary: "text-blue-500",
};

export function StatsCard({ label, value, icon, trend, trendUp, accent = "default" }: Props) {
  return (
    <div className={cn("rounded-xl border p-5 transition-all hover:shadow-md", accentStyles[accent])}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</span>
        {icon && <span className={iconAccentStyles[accent]}>{icon}</span>}
      </div>
      <div className="text-3xl font-bold text-gray-900 dark:text-white">{value}</div>
      {trend && (
        <div className={cn("text-xs mt-1", trendUp ? "text-green-500" : "text-red-500")}>
          {trend}
        </div>
      )}
    </div>
  );
}
