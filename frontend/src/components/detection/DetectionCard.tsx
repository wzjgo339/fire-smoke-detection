import type { DetectionResult } from "../../types/detection";
import { CLASS_COLORS } from "../../lib/constants";

interface Props {
  detection: DetectionResult;
  index: number;
}

export function DetectionCard({ detection, index }: Props) {
  const { bbox, class: clsName, confidence } = detection;
  const color = CLASS_COLORS[clsName] || "#999";
  const [x1, y1, x2, y2] = bbox;

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
      <span className="text-xs font-mono text-gray-400 w-5">#{index + 1}</span>
      <span
        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
        style={{ backgroundColor: color + "20", color }}
      >
        {clsName}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <div className="h-1.5 flex-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{ width: `${(confidence * 100).toFixed(0)}%`, backgroundColor: color }}
            />
          </div>
          <span className="text-xs font-mono text-gray-500 w-12 text-right">{(confidence * 100).toFixed(1)}%</span>
        </div>
      </div>
      <span className="text-[10px] font-mono text-gray-400 hidden sm:inline">
        ({x1.toFixed(0)},{y1.toFixed(0)})→({x2.toFixed(0)},{y2.toFixed(0)})
      </span>
    </div>
  );
}
