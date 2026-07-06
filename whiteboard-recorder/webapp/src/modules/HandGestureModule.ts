import type { HandResults, MediaPipeHands } from '../types/mediapipe';

const MEDIA_PIPE_CDN = 'https://cdn.jsdelivr.net/npm/@mediapipe';

interface HandGestureModuleOptions {
  videoElement: HTMLVideoElement;
  onMove?: (x: number, y: number) => void;
  onLandmarks?: (landmarks: Array<{ x: number; y: number; z: number }>) => void;
  onStatusChange?: (status: 'idle' | 'loading' | 'ready' | 'detected' | 'error', message?: string) => void;
  mirror?: boolean;
}

export class HandGestureModule {
  private videoElement: HTMLVideoElement;
  private onMove?: (x: number, y: number) => void;
  private onLandmarks?: (landmarks: Array<{ x: number; y: number; z: number }>) => void;
  private onStatusChange?: (status: 'idle' | 'loading' | 'ready' | 'detected' | 'error', message?: string) => void;
  private mirror: boolean;

  private hands: MediaPipeHands | null = null;
  private running = false;
  private rafId: number | null = null;
  private modelReady = false;
  private lastDetected = false;
  private loadError: string | null = null;
  private currentLandmarks: Array<{ x: number; y: number; z: number }> | null = null;

  constructor(options: HandGestureModuleOptions) {
    this.videoElement = options.videoElement;
    this.onMove = options.onMove;
    this.onLandmarks = options.onLandmarks;
    this.onStatusChange = options.onStatusChange;
    this.mirror = options.mirror ?? true;
  }

  setMirror(mirror: boolean): void {
    this.mirror = mirror;
  }

  private setStatus(status: 'idle' | 'loading' | 'ready' | 'detected' | 'error', message?: string): void {
    this.onStatusChange?.(status, message);
  }

  private loadScript(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = src;
      script.crossOrigin = 'anonymous';
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load ${src}`));
      document.head.appendChild(script);
    });
  }

  private async loadMediaPipe(): Promise<void> {
    if (typeof window === 'undefined' || !window.Hands) {
      this.setStatus('loading', '正在加载手势识别模型…');
      await this.loadScript(`${MEDIA_PIPE_CDN}/control_utils/control_utils.js`);
      await this.loadScript(`${MEDIA_PIPE_CDN}/drawing_utils/drawing_utils.js`);
      await this.loadScript(`${MEDIA_PIPE_CDN}/hands/hands.js`);
    }

    if (!window.Hands) {
      throw new Error('MediaPipe Hands 加载失败');
    }
  }

  async start(): Promise<void> {
    if (this.running) return;

    try {
      await this.loadMediaPipe();

      this.hands = new window.Hands({
        locateFile: (file) => `${MEDIA_PIPE_CDN}/hands/${file}`,
      });

      this.hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 0,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      this.hands.onResults((results: HandResults) => {
        if (!this.modelReady) {
          this.modelReady = true;
          this.setStatus('ready', '手势模型已就绪，请举起手');
        }

        const landmarks = results.multiHandLandmarks?.[0];
        if (landmarks) {
          this.currentLandmarks = landmarks;
          this.onLandmarks?.(landmarks);

          const tip = landmarks[8];
          let x = tip.x;
          if (this.mirror) {
            x = 1 - x;
          }
          this.onMove?.(x, tip.y);

          if (!this.lastDetected) {
            this.lastDetected = true;
            this.setStatus('detected', '已检测到手势');
          }
        } else {
          this.currentLandmarks = null;
          if (this.lastDetected) {
            this.lastDetected = false;
            this.setStatus('ready', '未检测到手，请举起手');
          }
        }
      });

      this.running = true;
      this.setStatus('loading', '正在启动手势追踪…');
      this.loop();
    } catch (err) {
      this.loadError = err instanceof Error ? err.message : String(err);
      this.setStatus('error', this.loadError);
      console.error('[HandGestureModule]', err);
    }
  }

  private loop = async (): Promise<void> => {
    if (!this.running) return;

    try {
      if (this.videoElement.readyState >= 2 && this.hands) {
        await this.hands.send({ image: this.videoElement });
      }
    } catch (err) {
      console.error('[HandGestureModule] send error:', err);
    }

    this.rafId = requestAnimationFrame(() => this.loop());
  };

  stop(): void {
    this.running = false;
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    if (this.hands) {
      this.hands.close();
      this.hands = null;
    }
    this.modelReady = false;
    this.lastDetected = false;
    this.setStatus('idle');
  }

  isRunning(): boolean {
    return this.running;
  }

  isModelReady(): boolean {
    return this.modelReady;
  }

  getCurrentLandmarks(): Array<{ x: number; y: number; z: number }> | null {
    return this.currentLandmarks;
  }

  getError(): string | null {
    return this.loadError;
  }

  destroy(): void {
    this.stop();
  }
}
