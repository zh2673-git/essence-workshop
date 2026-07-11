import { RecordingSettings, RecordingStatus, getResolutionDimensions } from '../types';
import { getSupportedMimeType } from '../utils/mediaUtils';

interface RecordingControllerOptions {
  getVideoStream: () => Promise<MediaStream> | MediaStream;
  getAudioStream: () => MediaStream | null;
  onStatusChange?: (status: RecordingStatus) => void;
  onTimeUpdate?: (elapsedSeconds: number) => void;
  onError?: (error: string) => void;
}

export class RecordingController {
  private options: RecordingControllerOptions;
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];
  private stream: MediaStream | null = null;
  private status: RecordingStatus = 'idle';
  private startTime = 0;
  private pausedTime = 0;
  private totalPausedDuration = 0;
  private timerInterval: number | null = null;
  private settings: RecordingSettings;

  constructor(options: RecordingControllerOptions, settings: RecordingSettings) {
    this.options = options;
    this.settings = settings;
  }

  private setStatus(status: RecordingStatus): void {
    this.status = status;
    this.options.onStatusChange?.(status);
  }

  updateSettings(settings: Partial<RecordingSettings>): void {
    this.settings = { ...this.settings, ...settings };
  }

  async startRecording(): Promise<void> {
    if (this.status !== 'idle' && this.status !== 'done' && this.status !== 'error') {
      throw new Error(`Cannot start recording from status: ${this.status}`);
    }

    this.recordedChunks = [];
    this.totalPausedDuration = 0;

    try {
      const videoStream = await this.options.getVideoStream();
      const audioStream = this.settings.audioEnabled ? this.options.getAudioStream() : null;

      this.stream = new MediaStream();
      videoStream.getVideoTracks().forEach((track) => {
        this.stream!.addTrack(track);
      });
      if (audioStream) {
        audioStream.getAudioTracks().forEach((track) => {
          this.stream!.addTrack(track);
        });
      }

      const mimeType = getSupportedMimeType();
      if (!mimeType) {
        throw new Error('MediaRecorder is not supported in this browser');
      }

      const { width, height } = getResolutionDimensions(this.settings.resolution);
      const pixelCount = width * height;
      let videoBitsPerSecond: number;
      if (pixelCount >= 3840 * 2160) {
        videoBitsPerSecond = 25000000;
      } else if (pixelCount >= 2560 * 1440) {
        videoBitsPerSecond = 12000000;
      } else if (pixelCount >= 1920 * 1080) {
        videoBitsPerSecond = 8000000;
      } else {
        videoBitsPerSecond = 5000000;
      }

      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType,
        videoBitsPerSecond,
      });

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          this.recordedChunks.push(e.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder?.mimeType || 'video/webm';
        const blob = new Blob(this.recordedChunks, { type: mimeType });
        this.cleanup();
        this.setStatus('done');
        if (this.onRecordingComplete) {
          this.onRecordingComplete(blob);
        }
      };

      this.mediaRecorder.onerror = (e) => {
        console.error('MediaRecorder error:', e);
        this.setStatus('error');
        this.options.onError?.('Recording error occurred');
        this.cleanup();
      };

      this.startTime = performance.now();
      this.mediaRecorder.start(1000);
      this.setStatus('recording');
      this.startTimer();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
      this.setStatus('error');
      this.options.onError?.(errorMessage);
      this.cleanup();
    }
  }

  private onRecordingComplete: ((blob: Blob) => void) | null = null;

  waitForRecordingComplete(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (this.status === 'done' && this.recordedChunks.length > 0) {
        const mimeType = this.mediaRecorder?.mimeType || 'video/webm';
        const blob = new Blob(this.recordedChunks, { type: mimeType });
        resolve(blob);
        return;
      }

      const originalOnComplete = this.onRecordingComplete;
      this.onRecordingComplete = (blob) => {
        originalOnComplete?.(blob);
        resolve(blob);
      };

      const originalOnError = this.options.onError;
      this.options.onError = (error) => {
        originalOnError?.(error);
        reject(new Error(error));
      };
    });
  }

  pauseRecording(): void {
    if (this.status !== 'recording') return;
    this.mediaRecorder?.pause();
    this.pausedTime = performance.now();
    this.stopTimer();
    this.setStatus('paused');
  }

  resumeRecording(): void {
    if (this.status !== 'paused') return;
    this.mediaRecorder?.resume();
    this.totalPausedDuration += performance.now() - this.pausedTime;
    this.startTimer();
    this.setStatus('recording');
  }

  async stopRecording(): Promise<Blob> {
    if (this.status !== 'recording' && this.status !== 'paused') {
      throw new Error(`Cannot stop recording from status: ${this.status}`);
    }

    this.setStatus('processing');
    this.stopTimer();

    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No active recording'));
        return;
      }

      const recorder = this.mediaRecorder;
      const originalOnStop = recorder.onstop;
      recorder.onstop = () => {
        if (originalOnStop) {
          originalOnStop.call(recorder, new Event('stop'));
        }
        const mimeType = recorder.mimeType || 'video/webm';
        const blob = new Blob(this.recordedChunks, { type: mimeType });
        resolve(blob);
      };

      recorder.stop();
    });
  }

  private startTimer(): void {
    this.stopTimer();
    this.timerInterval = window.setInterval(() => {
      const now = performance.now();
      const elapsed = (now - this.startTime - this.totalPausedDuration) / 1000;
      this.options.onTimeUpdate?.(elapsed);
    }, 100);
  }

  private stopTimer(): void {
    if (this.timerInterval !== null) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  private cleanup(): void {
    this.stopTimer();
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
    this.mediaRecorder = null;
  }

  getStatus(): RecordingStatus {
    return this.status;
  }

  reset(): void {
    this.cleanup();
    this.recordedChunks = [];
    this.setStatus('idle');
  }

  destroy(): void {
    this.cleanup();
  }
}
