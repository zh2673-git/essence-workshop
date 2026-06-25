import { useEffect, useRef } from 'react';
import { X, Download, RotateCcw } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { formatDuration, formatFileSize, generateFilename, getSupportedMimeType } from '../utils/mediaUtils';

interface PreviewModalProps {
  onReset: () => void;
}

export function PreviewModal({ onReset }: PreviewModalProps) {
  const { recordedBlob, recordedUrl, elapsedTime, setRecordedUrl } = useAppStore();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (recordedBlob && !recordedUrl) {
      const url = URL.createObjectURL(recordedBlob);
      setRecordedUrl(url);
    }

    return () => {
      if (recordedUrl) {
        URL.revokeObjectURL(recordedUrl);
      }
    };
  }, [recordedBlob, recordedUrl, setRecordedUrl]);

  const handleDownload = () => {
    if (!recordedUrl || !recordedBlob) return;

    const mimeType = getSupportedMimeType();
    const filename = generateFilename(mimeType);
    const a = document.createElement('a');
    a.href = recordedUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleReset = () => {
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl);
    }
    onReset();
  };

  if (!recordedBlob) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">录制完成</h2>
          <button
            onClick={handleReset}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div className="flex-1 p-4 overflow-auto bg-gray-50">
          {recordedUrl && (
            <video
              ref={videoRef}
              src={recordedUrl}
              controls
              className="w-full rounded-lg shadow-lg bg-black"
            />
          )}

          <div className="mt-4 flex items-center justify-center gap-8 text-gray-600">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-800">
                {formatDuration(elapsedTime)}
              </div>
              <div className="text-sm text-gray-500">录制时长</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-800">
                {formatFileSize(recordedBlob.size)}
              </div>
              <div className="text-sm text-gray-500">文件大小</div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t flex gap-3 justify-end">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
            重新录制
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors"
          >
            <Download className="w-5 h-5" />
            下载视频
          </button>
        </div>
      </div>
    </div>
  );
}
