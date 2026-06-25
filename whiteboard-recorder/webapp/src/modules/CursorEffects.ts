import { lerp } from '../utils/mathUtils';

interface Ripple {
  x: number;
  y: number;
  startTime: number;
  duration: number;
}

interface CursorStyle {
  color: string;
  size: number;
  showClickEffect: boolean;
  clickEffectColor: string;
}

export class CursorEffects {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private container: HTMLElement;
  private rafId: number | null = null;
  private running = false;

  private style: CursorStyle = {
    color: '#fbbf24',
    size: 20,
    showClickEffect: true,
    clickEffectColor: '#f97316',
  };

  private targetX = 0;
  private targetY = 0;
  private currentX = 0;
  private currentY = 0;
  private ripples: Ripple[] = [];

  private onMouseMove = (e: MouseEvent): void => {
    const rect = this.container.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    this.targetX = (e.clientX - rect.left) * scaleX;
    this.targetY = (e.clientY - rect.top) * scaleY;
  };

  private onMouseDown = (e: MouseEvent): void => {
    if (!this.style.showClickEffect) return;
    const rect = this.container.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    this.ripples.push({
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
      startTime: performance.now(),
      duration: 500,
    });
  };

  constructor(canvas: HTMLCanvasElement, container: HTMLElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.container = container;

    container.addEventListener('mousemove', this.onMouseMove);
    container.addEventListener('mousedown', this.onMouseDown);
  }

  setStyle(style: Partial<CursorStyle>): void {
    this.style = { ...this.style, ...style };
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
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  setSize(width: number, height: number): void {
    this.canvas.width = width;
    this.canvas.height = height;
  }

  getCanvas(): HTMLCanvasElement {
    return this.canvas;
  }

  private render = (): void => {
    if (!this.running) return;

    const { ctx, canvas, style } = this;
    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);

    this.currentX = lerp(this.currentX, this.targetX, 0.15);
    this.currentY = lerp(this.currentY, this.targetY, 0.15);

    const now = performance.now();
    this.ripples = this.ripples.filter((ripple) => {
      const elapsed = now - ripple.startTime;
      if (elapsed > ripple.duration) return false;

      const progress = elapsed / ripple.duration;
      const radius = style.size * (1 + progress * 3);
      const alpha = 1 - progress;

      ctx.beginPath();
      ctx.arc(ripple.x, ripple.y, radius, 0, Math.PI * 2);
      ctx.strokeStyle = style.clickEffectColor;
      ctx.lineWidth = 3 * (1 - progress);
      ctx.globalAlpha = alpha * 0.8;
      ctx.stroke();
      ctx.globalAlpha = 1;

      return true;
    });

    const gradient = ctx.createRadialGradient(
      this.currentX,
      this.currentY,
      0,
      this.currentX,
      this.currentY,
      style.size
    );
    gradient.addColorStop(0, style.color + 'cc');
    gradient.addColorStop(0.5, style.color + '66');
    gradient.addColorStop(1, style.color + '00');

    ctx.beginPath();
    ctx.arc(this.currentX, this.currentY, style.size, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(this.currentX, this.currentY, style.size * 0.15, 0, Math.PI * 2);
    ctx.fillStyle = style.color;
    ctx.fill();

    this.rafId = requestAnimationFrame(this.render);
  };

  destroy(): void {
    this.stop();
    this.container.removeEventListener('mousemove', this.onMouseMove);
    this.container.removeEventListener('mousedown', this.onMouseDown);
  }
}
