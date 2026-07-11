import type { Bounds, WebcamCameraLayout } from '../types';

export class CompositionRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private width: number;
  private height: number;
  private rafId: number | null = null;
  private running = false;
  private renderFullComposition = false;

  private whiteboardCanvas: HTMLCanvasElement | null = null;
  private screenVideoElement: HTMLVideoElement | null = null;
  private webcamCanvas: HTMLCanvasElement | null = null;
  private cursorCanvas: HTMLCanvasElement | null = null;

  private webcamBounds: Bounds = { x: 1000, y: 520, width: 240, height: 180 };
  private webcamMirror = true;
  private webcamBorderRadius = 16;
  private webcamEnabled = true;
  private cursorEnabled = true;
  private webcamCameraMode = false;
  private webcamCameraLayout: WebcamCameraLayout = 'fullscreen';

  constructor(canvas: HTMLCanvasElement, width: number, height: number, renderFullComposition = false) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.width = width;
    this.height = height;
    this.renderFullComposition = renderFullComposition;
    canvas.width = width;
    canvas.height = height;
  }

  setSources(
    whiteboard: HTMLCanvasElement | null,
    webcam: HTMLCanvasElement | null,
    cursor: HTMLCanvasElement | null,
    screenVideo: HTMLVideoElement | null = null
  ): void {
    this.whiteboardCanvas = whiteboard;
    this.webcamCanvas = webcam;
    this.cursorCanvas = cursor;
    this.screenVideoElement = screenVideo;
  }

  setWebcamBounds(bounds: Bounds): void {
    this.webcamBounds = bounds;
  }

  setWebcamMirror(mirror: boolean): void {
    this.webcamMirror = mirror;
  }

  setWebcamBorderRadius(radius: number): void {
    this.webcamBorderRadius = radius;
  }

  setWebcamEnabled(enabled: boolean): void {
    this.webcamEnabled = enabled;
  }

  setCursorEnabled(enabled: boolean): void {
    this.cursorEnabled = enabled;
  }

  setWebcamCameraMode(enabled: boolean): void {
    this.webcamCameraMode = enabled;
  }

  setWebcamCameraLayout(layout: WebcamCameraLayout): void {
    this.webcamCameraLayout = layout;
  }

  setResolution(width: number, height: number): void {
    this.width = width;
    this.height = height;
    this.canvas.width = width;
    this.canvas.height = height;
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

    const { ctx, width, height } = this;
    ctx.clearRect(0, 0, width, height);

    if (this.webcamCameraMode && this.webcamCanvas) {
      if (this.webcamCameraLayout === 'fullscreen') {
        ctx.drawImage(this.webcamCanvas, 0, 0, width, height);
      } else {
        this.drawWebcamWithLayout(width, height);
      }
    } else if (this.screenVideoElement && this.screenVideoElement.readyState >= 2) {
      this.drawScreenVideo(width, height);
    } else if (this.renderFullComposition && this.whiteboardCanvas) {
      ctx.drawImage(this.whiteboardCanvas, 0, 0, width, height);
    }

    if (this.webcamEnabled && this.webcamCanvas && !this.webcamCameraMode) {
      this.drawWebcam();
    }

    if (this.cursorEnabled && this.cursorCanvas) {
      ctx.drawImage(this.cursorCanvas, 0, 0, width, height);
    }

    this.rafId = requestAnimationFrame(this.render);
  };

  private drawScreenVideo(width: number, height: number): void {
    if (!this.screenVideoElement) return;
    const { ctx } = this;
    const videoWidth = this.screenVideoElement.videoWidth;
    const videoHeight = this.screenVideoElement.videoHeight;
    if (!videoWidth || !videoHeight) return;

    const scale = Math.max(width / videoWidth, height / videoHeight);
    const drawWidth = videoWidth * scale;
    const drawHeight = videoHeight * scale;
    const drawX = (width - drawWidth) / 2;
    const drawY = (height - drawHeight) / 2;
    ctx.drawImage(this.screenVideoElement, drawX, drawY, drawWidth, drawHeight);
  }

  private drawWebcamWithLayout(width: number, height: number): void {
    if (!this.webcamCanvas) return;
    const { ctx } = this;

    // 1:1 像素映射：canvas 尺寸已由 App.tsx 按目标比例裁剪好，
    // 这里只需从全屏摄像头画面的中心裁剪出同等尺寸的区域，不放大不缩小。
    const sourceWidth = width;
    const sourceHeight = height;
    const sourceX = (this.webcamCanvas.width - sourceWidth) / 2;
    const sourceY = (this.webcamCanvas.height - sourceHeight) / 2;

    if (this.webcamMirror) {
      ctx.save();
      ctx.translate(width / 2, height / 2);
      ctx.scale(-1, 1);
      ctx.drawImage(
        this.webcamCanvas,
        sourceX,
        sourceY,
        sourceWidth,
        sourceHeight,
        -width / 2,
        -height / 2,
        width,
        height
      );
      ctx.restore();
    } else {
      ctx.drawImage(
        this.webcamCanvas,
        sourceX,
        sourceY,
        sourceWidth,
        sourceHeight,
        0,
        0,
        width,
        height
      );
    }
  }

  private drawWebcam(): void {
    if (!this.webcamCanvas) return;
    const { ctx } = this;
    const { x, y, width: w, height: h } = this.webcamBounds;
    const r = Math.min(this.webcamBorderRadius, w / 2, h / 2);

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.clip();

    if (this.webcamMirror) {
      ctx.save();
      ctx.translate(x + w / 2, y + h / 2);
      ctx.scale(-1, 1);
      ctx.drawImage(this.webcamCanvas, -w / 2, -h / 2, w, h);
      ctx.restore();
    } else {
      ctx.drawImage(this.webcamCanvas, x, y, w, h);
    }

    ctx.restore();

    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.8)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 4;
    ctx.strokeStyle = 'rgba(0,0,0,0)';
    ctx.lineWidth = 0;
    ctx.stroke();
    ctx.restore();
  }

  destroy(): void {
    this.stop();
  }
}
