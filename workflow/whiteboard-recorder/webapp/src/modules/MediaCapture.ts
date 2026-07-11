export class MediaCapture {
  private videoElement: HTMLVideoElement;
  private webcamStream: MediaStream | null = null;
  private audioStream: MediaStream | null = null;
  private videoPermission: PermissionState = 'prompt';
  private audioPermission: PermissionState = 'prompt';
  private captureResolution: { width: number; height: number } = { width: 1280, height: 720 };

  constructor(videoElement: HTMLVideoElement) {
    this.videoElement = videoElement;
    this.videoElement.muted = true;
    this.videoElement.playsInline = true;
    this.videoElement.autoplay = true;
  }

  setCaptureResolution(width: number, height: number): void {
    this.captureResolution = { width, height };
  }

  private getVideoConstraints(): MediaTrackConstraints {
    const { width, height } = this.captureResolution;
    return {
      width: { ideal: Math.min(width, 1280) },
      height: { ideal: Math.min(height, 960) },
      aspectRatio: { ideal: 4 / 3 },
      frameRate: { ideal: 30 },
      facingMode: 'user',
    };
  }

  async requestPermissions(
    enableVideo: boolean,
    enableAudio: boolean
  ): Promise<{ videoGranted: boolean; audioGranted: boolean }> {
    let videoGranted = false;
    let audioGranted = false;

    try {
      if (enableVideo) {
        this.webcamStream = await navigator.mediaDevices.getUserMedia({
          video: this.getVideoConstraints(),
          audio: false,
        });
        this.videoElement.srcObject = this.webcamStream;
        await this.videoElement.play();
        this.videoPermission = 'granted';
        videoGranted = true;
      }

      if (enableAudio) {
        this.audioStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
          video: false,
        });
        this.audioPermission = 'granted';
        audioGranted = true;
      }
    } catch (err) {
      console.error('Media permission error:', err);
      if (enableVideo && !this.webcamStream) {
        this.videoPermission = 'denied';
      }
      if (enableAudio && !this.audioStream) {
        this.audioPermission = 'denied';
      }
    }

    return { videoGranted, audioGranted };
  }

  getWebcamStream(): MediaStream | null {
    return this.webcamStream;
  }

  getAudioStream(): MediaStream | null {
    return this.audioStream;
  }

  getVideoElement(): HTMLVideoElement {
    return this.videoElement;
  }

  getVideoPermission(): PermissionState {
    return this.videoPermission;
  }

  getAudioPermission(): PermissionState {
    return this.audioPermission;
  }

  stopWebcam(): void {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach((t) => t.stop());
      this.webcamStream = null;
    }
    this.videoElement.srcObject = null;
    this.videoPermission = 'prompt';
  }

  stopAudio(): void {
    if (this.audioStream) {
      this.audioStream.getTracks().forEach((t) => t.stop());
      this.audioStream = null;
    }
    this.audioPermission = 'prompt';
  }

  stopAllTracks(): void {
    this.stopWebcam();
    this.stopAudio();
  }

  destroy(): void {
    this.stopAllTracks();
  }
}
