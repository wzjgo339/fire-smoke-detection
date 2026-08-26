import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileImage, FileVideo, X } from "lucide-react";
import { cn, formatBytes } from "../../lib/utils";

interface Props {
  accept: Record<string, string[]>;
  maxSize: number;
  onFile: (file: File) => void;
  disabled?: boolean;
  label?: string;
}

export function FileUploadZone({ accept, maxSize, onFile, disabled, label }: Props) {
  const [preview, setPreview] = useState<{ name: string; size: number; url?: string } | null>(null);

  const onDrop = useCallback(
    (files: File[]) => {
      if (files.length === 0) return;
      const f = files[0];
      setPreview({ name: f.name, size: f.size, url: f.type.startsWith("image/") ? URL.createObjectURL(f) : undefined });
      onFile(f);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
    disabled,
  });

  const clear = () => {
    if (preview?.url) URL.revokeObjectURL(preview.url);
    setPreview(null);
  };

  const isVideo = Object.values(accept).flat().some((e) => e.startsWith("video/"));

  return (
    <div>
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all",
          isDragActive
            ? "border-blue-400 bg-blue-50/50 dark:bg-blue-950/20"
            : "border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600 bg-gray-50/50 dark:bg-gray-900/50",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        {preview ? (
          <div className="space-y-3">
            {preview.url ? (
              <img src={preview.url} alt={preview.name} className="max-h-48 mx-auto rounded-lg object-contain" />
            ) : (
              <div className="flex justify-center">
                {isVideo ? <FileVideo className="w-12 h-12 text-gray-400" /> : <FileImage className="w-12 h-12 text-gray-400" />}
              </div>
            )}
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{preview.name}</p>
            <p className="text-xs text-gray-500">{formatBytes(preview.size)}</p>
            <button
              onClick={(e) => { e.stopPropagation(); clear(); }}
              className="inline-flex items-center gap-1 text-xs text-red-500 hover:underline"
            >
              <X className="w-3 h-3" /> 移除
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-10 h-10 mx-auto text-gray-400" />
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {isDragActive ? "释放以上传" : label || "拖放文件或点击选择"}
            </p>
            <p className="text-xs text-gray-500">
              最大 {formatBytes(maxSize)} · {Object.values(accept).flat().join(", ")}
            </p>
          </div>
        )}
      </div>
      {fileRejections.length > 0 && (
        <p className="mt-2 text-xs text-red-500">{fileRejections[0].errors[0]?.message || "文件不符合要求"}</p>
      )}
    </div>
  );
}
