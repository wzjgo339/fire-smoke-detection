import { useState, useCallback } from "react";
import { Loader2, Video, AlertTriangle } from "lucide-react";
import { PageHeader } from "../components/common/PageHeader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { EmptyState } from "../components/common/EmptyState";
import { FileUploadZone } from "../components/detection/FileUploadZone";
import { OptionsBar } from "../components/detection/OptionsBar";
import { VideoPlayer } from "../components/detection/VideoPlayer";
import { VideoTimeline } from "../components/detection/VideoTimeline";
import { DetectionList } from "../components/detection/DetectionList";
import { useDetectionStore } from "../stores/useDetectionStore";
import { usePolling } from "../hooks/usePolling";
import { MAX_VIDEO_SIZE, DEFAULT_CONFIDENCE, DEFAULT_IOU, VIDEO_POLL_INTERVAL } from "../lib/constants";
import { formatMs } from "../lib/utils";

export default function VideoDetection() {
  const [confidence, setConfidence] = useState(DEFAULT_CONFIDENCE);
  const [iou, setIou] = useState(DEFAULT_IOU);
  const [frameSkip, setFrameSkip] = useState(1);
  const [taskId, setTaskId] = useState<string | null>(null);
  const { isProcessing, error, currentVideoTask, uploadVideo, pollVideoStatus, clearError, resetResults } =
    useDetectionStore();

  const handleFile = async (file: File) => {
    resetResults();
    const tid = await uploadVideo(file, confidence, iou, frameSkip);
    if (tid) setTaskId(tid);
  };

  const pollCallback = useCallback(async () => {
    if (!taskId) return true;
    const done = await pollVideoStatus(taskId);
    return done;
  }, [taskId, pollVideoStatus]);

  usePolling(pollCallback, VIDEO_POLL_INTERVAL, !!taskId && currentVideoTask?.status === "processing");

  const maxTimelineCount = currentVideoTask?.timeline?.reduce((m, p) => Math.max(m, p.count), 0) || 0;

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader title="视频检测" description="上传视频进行逐帧火灾和烟雾分析" />

      {error && <ErrorAlert message={error} onDismiss={clearError} />}

      <div className="space-y-6">
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
          <FileUploadZone
            accept={{ "video/*": [".mp4", ".avi", ".mov", ".mkv", ".webm"] }}
            maxSize={MAX_VIDEO_SIZE}
            onFile={handleFile}
            disabled={isProcessing}
            label="拖放视频或点击选择"
          />
          <OptionsBar
            confidence={confidence} iou={iou}
            onConfidenceChange={setConfidence}
            onIouChange={setIou}
            disabled={isProcessing}
          />
          <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            帧跳过
            <input
              type="number" min={1} max={30}
              value={frameSkip}
              onChange={(e) => setFrameSkip(Math.max(1, parseInt(e.target.value) || 1))}
              disabled={isProcessing}
              className="w-16 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-700"
            />
          </label>
        </div>

        {/* Processing state */}
        {currentVideoTask?.status === "processing" && (
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">处理中...</p>
                <p className="text-xs text-gray-500">
                  {currentVideoTask.frames_processed} / {currentVideoTask.frames_total} 帧
                </p>
              </div>
            </div>
            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${currentVideoTask.progress_pct || 0}%` }}
              />
            </div>
            {currentVideoTask.current_fps && (
              <p className="text-xs text-gray-500">速度: {currentVideoTask.current_fps.toFixed(0)} FPS</p>
            )}
          </div>
        )}

        {/* Failed */}
        {currentVideoTask?.status === "failed" && (
          <div className="rounded-xl border border-red-200 dark:border-red-800 p-6 flex items-center gap-3 text-red-700 dark:text-red-300">
            <AlertTriangle className="w-5 h-5" />
            <span className="text-sm">处理失败: {currentVideoTask.error || "未知错误"}</span>
          </div>
        )}

        {/* Completed */}
        {currentVideoTask?.status === "completed" && currentVideoTask.annotated_url && (
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{currentVideoTask.filename}</p>
              <p className="text-xs text-gray-500">
                {currentVideoTask.total_frames} 帧 · 处理时间 {formatMs(currentVideoTask.processing_time_ms)}
              </p>
            </div>

            <div className="flex gap-2 text-xs">
              <span className="px-2 py-1 rounded bg-red-100 dark:bg-red-950/30 text-red-700 dark:text-red-300">
                Fire: {currentVideoTask.fire_count}
              </span>
              <span className="px-2 py-1 rounded bg-orange-100 dark:bg-orange-950/30 text-orange-700 dark:text-orange-300">
                Smoke: {currentVideoTask.smoke_count}
              </span>
              <span className="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                总检测: {currentVideoTask.total_detections}
              </span>
            </div>

            <VideoPlayer annotatedUrl={currentVideoTask.annotated_url} />
            <VideoTimeline timeline={currentVideoTask.timeline ?? null} maxCount={maxTimelineCount} />

            {currentVideoTask.results && currentVideoTask.results.length > 0 && (
              <details className="text-sm">
                <summary className="cursor-pointer font-medium text-gray-700 dark:text-gray-300">
                  查看关键帧 ({currentVideoTask.results.length})
                </summary>
                <div className="mt-3 space-y-4 max-h-80 overflow-y-auto">
                  {currentVideoTask.results.slice(0, 20).map((fr) => (
                    <div key={fr.frame_index} className="border-t pt-3">
                      <p className="text-xs text-gray-500 mb-2">
                        帧 {fr.frame_index} · {fr.timestamp_sec?.toFixed(1)}s
                      </p>
                      <DetectionList detections={fr.detections} />
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}

        {!isProcessing && !currentVideoTask && !error && (
          <EmptyState
            icon={<Video className="w-12 h-12" />}
            title="上传视频开始检测"
            description="支持 MP4、AVI、MOV、MKV、WebM 格式，最大 2GB"
          />
        )}
      </div>
    </div>
  );
}
