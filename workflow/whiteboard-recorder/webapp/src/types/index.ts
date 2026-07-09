export type RecordingStatus = 'idle' | 'countdown' | 'recording' | 'paused' | 'processing' | 'done' | 'error';

export type RecordingMode = 'whiteboard' | 'camera';

export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ExcalidrawElement {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  angle?: number;
  strokeColor?: string;
  backgroundColor?: string;
  fillStyle?: string;
  strokeWidth?: number;
  strokeStyle?: string;
  roughness?: number;
  opacity?: number;
  groupIds?: string[];
  seed?: number;
  version?: number;
  versionNonce?: number;
  isDeleted?: boolean;
  boundElements?: any[];
  updated?: number;
  link?: string | null;
  locked?: boolean;
  text?: string;
  fontSize?: number;
  fontFamily?: number;
  textAlign?: string;
  verticalAlign?: string;
  containerId?: string | null;
  originalText?: string;
  autoResize?: boolean;
  lineHeight?: number;
  points?: number[][];
  startBinding?: any;
  endBinding?: any;
  startArrowhead?: string | null;
  endArrowhead?: string | null;
  [key: string]: any;
}

export interface WhiteboardScene {
  id?: string;
  index?: number;
  title: string;
  scene_x?: number;
  viewport?: {
    x: number;
    y: number;
    zoom: number;
  };
  duration_estimate?: number;
  teleprompter_script: string;
  elements: ExcalidrawElement[];
}

export interface WhiteboardProject {
  version: string;
  title: string;
  created_at?: string;
  scene_spacing?: number;
  canvas_layout?: 'horizontal' | 'vertical';
  total_scenes?: number;
  scenes: WhiteboardScene[];
}

export interface WebcamSettings {
  enabled: boolean;
  mirror: boolean;
  bounds: Bounds;
  borderRadius: number;
  filter: 'none' | 'soften' | 'grayscale';
}

export interface CursorSettings {
  enabled: boolean;
  color: string;
  size: number;
  showClickEffect: boolean;
  clickEffectColor: string;
}

export interface GestureSettings {
  enabled: boolean;
  mirror: boolean;
  showPreview: boolean;
  size: number;
  color: string;
  icon: string;
}

export interface TeleprompterSettings {
  enabled: boolean;
  text: string;
  fontSize: number;
  speed: number;
  opacity: number;
  position: 'top' | 'bottom' | 'left' | 'right';
}

export interface RecordingSettings {
  resolution: '720p' | '1080p' | '2k';
  framerate: 30 | 60;
  countdownSeconds: number;
  audioEnabled: boolean;
  mode: RecordingMode;
  continuousTeleprompter: boolean;
}

export const RESOLUTION_MAP: Record<RecordingSettings['resolution'], { width: number; height: number }> = {
  '720p': { width: 1280, height: 720 },
  '1080p': { width: 1920, height: 1080 },
  '2k': { width: 2560, height: 1440 },
};

export const DEFAULT_WEBCAM_SETTINGS: WebcamSettings = {
  enabled: true,
  mirror: true,
  bounds: { x: 1000, y: 520, width: 240, height: 180 },
  borderRadius: 16,
  filter: 'soften',
};

export const DEFAULT_CURSOR_SETTINGS: CursorSettings = {
  enabled: true,
  color: '#fbbf24',
  size: 20,
  showClickEffect: true,
  clickEffectColor: '#f97316',
};

export const DEFAULT_GESTURE_SETTINGS: GestureSettings = {
  enabled: false,
  mirror: true,
  showPreview: false,
  size: 24,
  color: '#38bdf8',
  icon: '🚀',
};

export const DEFAULT_TELEPROMPTER_SETTINGS: TeleprompterSettings = {
  enabled: false,
  text: '',
  fontSize: 28,
  speed: 80,
  opacity: 0.7,
  position: 'right',
};

export const DEFAULT_RECORDING_SETTINGS: RecordingSettings = {
  resolution: '720p',
  framerate: 30,
  countdownSeconds: 3,
  audioEnabled: true,
  mode: 'whiteboard',
  continuousTeleprompter: false,
};
