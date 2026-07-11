export class ScreenCaptureModule {
  private videoElement: HTMLVideoElement;
  private screenStream: MediaStream | null = null;
  private running = false;
  private captureResolution: { width: number; height: number } = { width: 1920, height: 1080 };

  constructor(videoElement: HTMLVideoElement) {
    this.videoElement = videoElement;
    this.videoElement.muted = true;
    this.videoElement.playsInline = true;
    this.videoElement.autoplay = true;
  }

  setCaptureResolution(width: number, height: number): void {
    this.captureResolution = { width, height };
  }

  private getDisplayConstraints(): MediaTrackConstraints {
    const { width, height } = this.captureResolution;
    return {
      cursor: 'always',
      width: { ideal: width },
      height: { ideal: height },
      frameRate: { ideal: 30 },
    } as MediaTrackConstraints;
  }

  async requestScreen(): Promise<boolean> {
    try {
      this.screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: this.getDisplayConstraints(),
        audio: false,
      });

      this.videoElement.srcObject = this.screenStream;
      await this.videoElement.play();

      this.screenStream.getVideoTracks().forEach((track) => {
        track.onended = () => {
          this.stop();
        };
      });

      return true;
    } catch (err) {
      console.error('Screen capture error:', err);
      return false;
    }
  }

  start(): void {
    this.running = true;
  }

  stop(): void {
    this.running = false;
    if (this.screenStream) {
      this.screenStream.getTracks().forEach((t) => t.stop());
      this.screenStream = null;
    }
    this.videoElement.srcObject = null;
  }

  getVideoElement(): HTMLVideoElement {
    return this.videoElement;
  }

  getScreenStream(): MediaStream | null {
    return this.screenStream;
  }

  isRunning(): boolean {
    return this.running;
  }

  destroy(): void {
    this.stop();
  }
}
