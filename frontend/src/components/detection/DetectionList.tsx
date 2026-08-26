import type { DetectionResult } from "../../types/detection";
import { DetectionCard } from "./DetectionCard";

interface Props {
  detections: DetectionResult[];
}

export function DetectionList({ detections }: Props) {
  if (detections.length === 0) return null;
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
        检测结果 ({detections.length})
      </h3>
      {detections.map((d, i) => (
        <DetectionCard key={i} detection={d} index={i} />
      ))}
    </div>
  );
}
