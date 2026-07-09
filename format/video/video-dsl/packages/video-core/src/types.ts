export interface CompositionConfig {
  id: string;
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
}

export interface SequenceContextValue {
  cumulatedFrom: number;
  parentFrom: number;
}

export interface TimelineContextValue {
  currentFrame: number;
  composition: CompositionConfig;
}

export interface AssetRegistry {
  images: Set<string>;
  audio: Set<string>;
  video: Set<string>;
}

export interface InterpolateOptions {
  easing?: (t: number) => number;
  extrapolateLeft?: 'extend' | 'clamp' | 'identity';
  extrapolateRight?: 'extend' | 'clamp' | 'identity';
}
