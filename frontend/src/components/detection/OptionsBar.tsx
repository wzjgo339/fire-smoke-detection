interface Props {
  confidence: number;
  iou: number;
  onConfidenceChange: (v: number) => void;
  onIouChange: (v: number) => void;
  disabled?: boolean;
}

export function OptionsBar({ confidence, iou, onConfidenceChange, onIouChange, disabled }: Props) {
  return (
    <div className="flex flex-wrap gap-4">
      <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        置信度 <span className="font-mono text-xs w-8">{confidence.toFixed(2)}</span>
        <input
          type="range" min="0.05" max="0.95" step="0.05"
          value={confidence}
          onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
          disabled={disabled}
          className="w-24 h-1.5 accent-blue-500"
        />
      </label>
      <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        IoU <span className="font-mono text-xs w-8">{iou.toFixed(2)}</span>
        <input
          type="range" min="0.1" max="0.9" step="0.05"
          value={iou}
          onChange={(e) => onIouChange(parseFloat(e.target.value))}
          disabled={disabled}
          className="w-24 h-1.5 accent-blue-500"
        />
      </label>
    </div>
  );
}
