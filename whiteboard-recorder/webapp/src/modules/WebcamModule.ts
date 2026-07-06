import type { Bounds } from '../types';
import type { HandGestureModule } from './HandGestureModule';

export class WebcamModule {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private videoElement: HTMLVideoElement;
  private rafId: number | null = null;
  private running = false;
  private filter: 'none' | 'soften' | 'grayscale' = 'none';
  private gestureEnabled = false;
  private handGestureModule: HandGestureModule | null = null;

  private bounds: Bounds = { x: 0, y: 0, width: 320, height: 240 };

  constructor(canvas: HTMLCanvasElement, videoElement: HTMLVideoElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.videoElement = videoElement;
    this.canvas.width = 320;
    this.canvas.height = 240;
  }

  setGestureMode(enabled: boolean, module: HandGestureModule | null): void {
    this.gestureEnabled = enabled;
    this.handGestureModule = module;
  }

  setBounds(bounds: Bounds): void {
    this.bounds = bounds;
  }

  getBounds(): Bounds {
    return { ...this.bounds };
  }

  setMirror(_mirror: boolean): void {
  }

  setFilter(filter: 'none' | 'soften' | 'grayscale'): void {
    this.filter = filter;
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    this.render();
  }

  stop(): void {
    this.running = false;
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  getCanvas(): HTMLCanvasElement {
    return this.canvas;
  }

  private render = (): void => {
    if (!this.running) return;

    const { ctx, videoElement, canvas } = this;
    const { width, height } = canvas;

    ctx.clearRect(0, 0, width, height);

    if (videoElement.readyState >= 2) {
      ctx.save();

      switch (this.filter) {
        case 'soften':
          ctx.filter = 'blur(0.5px) brightness(1.05) contrast(1.05)';
          break;
        case 'grayscale':
          ctx.filter = 'grayscale(1)';
          break;
        default:
          ctx.filter = 'none';
      }

      const videoWidth = videoElement.videoWidth;
      const videoHeight = videoElement.videoHeight;
      if (videoWidth && videoHeight) {
        const scale = Math.max(width / videoWidth, height / videoHeight);
        const drawWidth = videoWidth * scale;
        const drawHeight = videoHeight * scale;
        const drawX = (width - drawWidth) / 2;
        const drawY = (height - drawHeight) / 2;
        ctx.drawImage(videoElement, drawX, drawY, drawWidth, drawHeight);

        if (this.gestureEnabled) {
          this.drawLandmarks(drawX, drawY, drawWidth, drawHeight);
        }
      }

      ctx.restore();
    }

    this.rafId = requestAnimationFrame(this.render);
  };

  private drawLandmarks(drawX: number, drawY: number, drawWidth: number, drawHeight: number): void {
    const landmarks = this.handGestureModule?.getCurrentLandmarks();
    if (!landmarks || landmarks.length === 0) return;

    const { ctx } = this;

    ctx.save();
    ctx.filter = 'none';

    for (let i = 0; i < landmarks.length; i++) {
      const p = landmarks[i];
      const x = drawX + p.x * drawWidth;
      const y = drawY + p.y * drawHeight;
      const isIndexTip = i === 8;

      ctx.beginPath();
      ctx.arc(x, y, isIndexTip ? 5 : 2.5, 0, Math.PI * 2);
      ctx.fillStyle = isIndexTip ? '#ef4444' : '#4ade80';
      ctx.fill();

      if (isIndexTip) {
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }

    ctx.restore();
  }

  destroy(): void {
    this.stop();
  }
}
