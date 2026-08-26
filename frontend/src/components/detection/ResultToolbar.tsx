import { Download } from "lucide-react";

interface Props {
  annotatedUrl: string | null;
  filename: string;
}

export function ResultToolbar({ annotatedUrl, filename }: Props) {
  const handleDownload = () => {
    if (!annotatedUrl) return;
    const a = document.createElement("a");
    a.href = annotatedUrl;
    a.download = `annotated_${filename}`;
    a.click();
  };

  return (
    <div className="flex items-center gap-2">
      {annotatedUrl && (
        <button onClick={handleDownload} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors">
          <Download className="w-3.5 h-3.5" /> 下载标注图
        </button>
      )}
    </div>
  );
}
