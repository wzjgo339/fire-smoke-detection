import { useState } from "react";
import { cn } from "../../lib/utils";

interface Props {
  originalUrl: string | null;
  annotatedUrl: string | null;
  filename: string;
}

type Tab = "annotated" | "side-by-side";

export function ImageDisplay({ originalUrl, annotatedUrl, filename }: Props) {
  const [tab, setTab] = useState<Tab>("annotated");

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        {(["annotated", "side-by-side"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
              tab === t
                ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
                : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            )}
          >
            {t === "annotated" ? "标注视图" : "并排对比"}
          </button>
        ))}
      </div>

      {tab === "annotated" && annotatedUrl && (
        <img src={annotatedUrl} alt={filename} className="w-full rounded-lg border border-gray-200 dark:border-gray-800" />
      )}

      {tab === "side-by-side" && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-400 mb-1 text-center">原始图像</p>
            {originalUrl && <img src={originalUrl} alt="原始" className="w-full rounded-lg border" />}
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 text-center">检测结果</p>
            {annotatedUrl && <img src={annotatedUrl} alt="标注" className="w-full rounded-lg border" />}
          </div>
        </div>
      )}
    </div>
  );
}
