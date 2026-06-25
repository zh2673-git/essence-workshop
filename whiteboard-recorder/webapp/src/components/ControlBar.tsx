import { Play, Pause, Square, Settings as SettingsIcon, Video, VideoOff, Mic, MicOff, MousePointer, MousePointerClick, FileText } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { formatDuration } from '../utils/mediaUtils';

interface ControlBarProps {
  onStartRecording: () => void;
  onPauseRecording: () => void;
  onResumeRecording: () => void;
  onStopRecording: () => void;
}

export function ControlBar({
  onStartRecording,
  onPauseRecording,
  onResumeRecording,
  onStopRecording,
}: ControlBarProps) {
  const {
    status,
    elapsedTime,
    webcam,
    cursor,
    teleprompter,
    recording,
    updateWebcamSettings,
    updateCursorSettings,
    updateTeleprompterSettings,
    updateRecordingSettings,
    toggleSettings,
  } = useAppStore();

  const isRecording = status === 'recording';
  const isPaused = status === 'paused';
  const isIdle = status === 'idle' || status === 'done' || status === 'error';

  const handleRecordClick = () => {
    if (isIdle) {
      onStartRecording();
    } else if (isRecording) {
      onPauseRecording();
    } else if (isPaused) {
      onResumeRecording();
    }
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40">
      <div className="flex items-center gap-2 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl px-4 py-3 border border-gray-200">
        <button
          onClick={() => toggleSettings('recording')}
          className="p-3 rounded-xl hover:bg-gray-100 text-gray-600 transition-colors"
          title="设置"
        >
          <SettingsIcon className="w-5 h-5" />
        </button>

        <div className="w-px h-8 bg-gray-200" />

        <button
          onClick={() => updateWebcamSettings({ enabled: !webcam.enabled })}
          className={`p-3 rounded-xl transition-colors ${
            webcam.enabled
              ? 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={webcam.enabled ? '关闭摄像头' : '开启摄像头'}
        >
          {webcam.enabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
        </button>

        <button
          onClick={() => updateRecordingSettings({ audioEnabled: !recording.audioEnabled })}
          className={`p-3 rounded-xl transition-colors ${
            recording.audioEnabled
              ? 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={recording.audioEnabled ? '关闭麦克风' : '开启麦克风'}
        >
          {recording.audioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
        </button>

        <button
          onClick={() => updateCursorSettings({ enabled: !cursor.enabled })}
          className={`p-3 rounded-xl transition-colors ${
            cursor.enabled
              ? 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={cursor.enabled ? '关闭光标高亮' : '开启光标高亮'}
        >
          {cursor.enabled ? <MousePointerClick className="w-5 h-5" /> : <MousePointer className="w-5 h-5" />}
        </button>

        <button
          onClick={() => updateTeleprompterSettings({ enabled: !teleprompter.enabled })}
          className={`p-3 rounded-xl transition-colors ${
            teleprompter.enabled
              ? 'bg-purple-100 text-purple-600 hover:bg-purple-200'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={teleprompter.enabled ? '关闭提词器' : '开启提词器'}
        >
          <FileText className="w-5 h-5" />
        </button>

        <div className="w-px h-8 bg-gray-200" />

        {(isRecording || isPaused) && (
          <div className="flex items-center gap-2 px-3">
            <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-yellow-500'}`} />
            <span className="font-mono text-lg font-semibold text-gray-700 min-w-[60px]">
              {formatDuration(elapsedTime)}
            </span>
          </div>
        )}

        <button
          onClick={handleRecordClick}
          disabled={status === 'countdown' || status === 'processing'}
          className={`p-4 rounded-full transition-all ${
            isRecording || isPaused
              ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
              : 'bg-red-500 hover:bg-red-600 text-white'
          } disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl`}
          title={isIdle ? '开始录制' : isRecording ? '暂停' : '继续'}
        >
          {isIdle ? (
            <div className="w-5 h-5 rounded-full bg-white ml-0.5" />
          ) : isRecording ? (
            <Pause className="w-5 h-5" />
          ) : isPaused ? (
            <Play className="w-5 h-5 ml-0.5" />
          ) : (
            <div className="w-5 h-5 rounded-full bg-white" />
          )}
        </button>

        {(isRecording || isPaused) && (
          <button
            onClick={onStopRecording}
            className="p-4 rounded-full bg-gray-700 hover:bg-gray-800 text-white transition-colors shadow-lg"
            title="停止录制"
          >
            <Square className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
}
