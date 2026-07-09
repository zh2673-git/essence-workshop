export interface RenderOptions {
  entryFile: string;
  outputDir?: string;
  publicDir?: string;
  width?: number;
  height?: number;
  fps?: number;
  durationInFrames?: number;
  deviceScaleFactor?: number;
  format?: 'mp4' | 'gif';
  quality?: 'draft' | 'medium' | 'high';
  audioPath?: string;
  bgmPath?: string;
  onProgress?: (progress: RenderProgress) => void;
}

export interface RenderProgress {
  currentFrame: number;
  totalFrames: number;
  phase: 'bundle' | 'screenshot' | 'audio' | 'encode' | 'done';
}

export interface RenderResult {
  videoPath: string;
  framesDir: string;
  audioPath?: string;
  durationInSeconds: number;
}
