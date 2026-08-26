import { useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { PageHeader } from "../components/common/PageHeader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { EmptyState } from "../components/common/EmptyState";
import { FileUploadZone } from "../components/detection/FileUploadZone";
import { OptionsBar } from "../components/detection/OptionsBar";
import { ImageDisplay } from "../components/detection/ImageDisplay";
import { DetectionList } from "../components/detection/DetectionList";
import { ResultToolbar } from "../components/detection/ResultToolbar";
import { useDetectionStore } from "../stores/useDetectionStore";
import { MAX_IMAGE_SIZE, DEFAULT_CONFIDENCE, DEFAULT_IOU } from "../lib/constants";
import { formatMs } from "../lib/utils";

export default function ImageDetection() {
  const [confidence, setConfidence] = useState(DEFAULT_CONFIDENCE);
  const [iou, setIou] = useState(DEFAULT_IOU);
  const { isProcessing, uploadProgress, error, currentImageResult, uploadAndDetectImage, clearError, resetResults } =
    useDetectionStore();

  const handleFile = async (file: File) => {
    resetResults();
    await uploadAndDetectImage(file, confidence, iou);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader title="图像检测" description="上传图像进行火灾和烟雾检测" />

      {error && <ErrorAlert message={error} onDismiss={clearError} />}

      <div className="space-y-6">
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
          <FileUploadZone
            accept={{ "image/*": [".jpg", ".jpeg", ".png", ".bmp", ".webp"] }}
            maxSize={MAX_IMAGE_SIZE}
            onFile={handleFile}
            disabled={isProcessing}
            label="拖放图片或点击选择"
          />
          <OptionsBar
            confidence={confidence} iou={iou}
            onConfidenceChange={setConfidence}
            onIouChange={setIou}
            disabled={isProcessing}
          />
        </div>

        {isProcessing && (
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-8 text-center space-y-3">
            <Loader2 className="w-8 h-8 mx-auto animate-spin text-blue-500" />
            <p className="text-sm text-gray-500">正在推理中...</p>
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="w-64 mx-auto h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
              </div>
            )}
          </div>
        )}

        {currentImageResult && (
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{currentImageResult.filename}</p>
                <p className="text-xs text-gray-500">
                  {currentImageResult.image_width}x{currentImageResult.image_height} · {formatMs(currentImageResult.processing_time_ms)}
                </p>
              </div>
              <ResultToolbar annotatedUrl={currentImageResult.annotated_url} filename={currentImageResult.filename} />
            </div>

            <ImageDisplay
              originalUrl={currentImageResult.original_url}
              annotatedUrl={currentImageResult.annotated_url}
              filename={currentImageResult.filename}
            />

            <div className="flex gap-3 text-sm">
              <span className="px-2 py-1 rounded bg-red-100 dark:bg-red-950/30 text-red-700 dark:text-red-300 text-xs font-medium">
                Fire: {currentImageResult.fire_count}
              </span>
              <span className="px-2 py-1 rounded bg-orange-100 dark:bg-orange-950/30 text-orange-700 dark:text-orange-300 text-xs font-medium">
                Smoke: {currentImageResult.smoke_count}
              </span>
            </div>

            <DetectionList detections={currentImageResult.detections} />
          </div>
        )}

        {!isProcessing && !currentImageResult && !error && (
          <EmptyState
            icon={<Upload className="w-12 h-12" />}
            title="上传图片开始检测"
            description="支持 JPG、PNG、BMP、WebP 格式，最大 20MB"
          />
        )}
      </div>
    </div>
  );
}
