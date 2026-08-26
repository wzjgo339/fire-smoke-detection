import type { TimelinePoint } from "../../types/detection";

interface Props {
  timeline: TimelinePoint[] | null;
  maxCount: number;
}

export function VideoTimeline({ timeline, maxCount }: Props) {
  if (!timeline || timeline.length === 0) return null;

  const h = 60;
  const peak = maxCount || 1;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">检测时间线</h3>
      <div className="flex items-end gap-0.5 h-[60px]">
        {timeline.map((pt, i) => {
          const barH = Math.max(3, (pt.count / peak) * h);
          return (
            <div
              key={i}
              className="flex-1 bg-fire/70 dark:bg-fire/50 rounded-t min-w-[2px]"
              style={{ height: `${barH}px` }}
              title={`${pt.t.toFixed(1)}s: ${pt.count} detections`}
            />
          );
        })}
      </div>
      <div className="flex justify-between text-[10px] text-gray-400">
        <span>0s</span>
        <span>{timeline.length > 0 ? timeline[timeline.length - 1].t.toFixed(0) + "s" : ""}</span>
      </div>
    </div>
  );
}
