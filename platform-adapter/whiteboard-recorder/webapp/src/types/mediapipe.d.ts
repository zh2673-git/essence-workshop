declare global {
  interface Window {
    Hands: new (config: { locateFile: (file: string) => string }) => MediaPipeHands;
    Camera: any;
    drawConnectors: any;
    drawLandmarks: any;
  }
}

export interface MediaPipeHands {
  setOptions(options: {
    maxNumHands?: number;
    modelComplexity?: 0 | 1 | 2;
    minDetectionConfidence?: number;
    minTrackingConfidence?: number;
  }): void;
  onResults(callback: (results: HandResults) => void): void;
  send(input: { image: HTMLVideoElement | HTMLImageElement | HTMLCanvasElement }): Promise<void>;
  close(): Promise<void>;
}

export interface HandResults {
  multiHandLandmarks?: HandLandmark[][];
  multiHandedness?: Array<{ label: string; score: number }>;
}

export interface HandLandmark {
  x: number;
  y: number;
  z: number;
}

export {};
