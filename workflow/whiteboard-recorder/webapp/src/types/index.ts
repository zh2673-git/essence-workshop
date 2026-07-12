export type RecordingStatus = 'idle' | 'countdown' | 'recording' | 'paused' | 'processing' | 'done' | 'error';

export type RecordingMode = 'whiteboard' | 'camera' | 'screen';

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

export type WebcamCameraLayout = 'fullscreen' | '16:9' | '9:16' | '4:3' | '1:1';

export function getCameraLayoutDimensions(layout: WebcamCameraLayout, baseWidth: number, baseHeight: number): { width: number; height: number } {
  if (layout === 'fullscreen') {
    return { width: baseWidth, height: baseHeight };
  }

  const ratioMap: Record<Exclude<WebcamCameraLayout, 'fullscreen'>, number> = {
    '16:9': 16 / 9,
    '9:16': 9 / 16,
    '4:3': 4 / 3,
    '1:1': 1,
  };
  const targetRatio = ratioMap[layout];
  const baseRatio = baseWidth / baseHeight;

  // 从 base 画面中按目标比例裁剪中心区域，保持原始像素密度，不放大缩小
  if (baseRatio > targetRatio) {
    const width = Math.round(baseHeight * targetRatio);
    return { width, height: baseHeight };
  }
  const height = Math.round(baseWidth / targetRatio);
  return { width: baseWidth, height };
}

export interface WebcamSettings {
  enabled: boolean;
  mirror: boolean;
  bounds: Bounds;
  borderRadius: number;
  filter: 'none' | 'soften' | 'grayscale';
  cameraLayout: WebcamCameraLayout;
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
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
}

export type RecordingResolution = 'auto' | '4k' | '2k' | '1080p' | '720p';

export interface RecordingSettings {
  resolution: RecordingResolution;
  framerate: 30 | 60;
  countdownSeconds: number;
  audioEnabled: boolean;
  mode: RecordingMode;
  continuousTeleprompter: boolean;
  recordFullInterface: boolean;
}

export const RESOLUTION_MAP: Record<Exclude<RecordingResolution, 'auto'>, { width: number; height: number }> = {
  '4k': { width: 3840, height: 2160 },
  '2k': { width: 2560, height: 1440 },
  '1080p': { width: 1920, height: 1080 },
  '720p': { width: 1280, height: 720 },
};

export function getResolutionDimensions(resolution: RecordingResolution): { width: number; height: number } {
  if (resolution === 'auto') {
    return RESOLUTION_MAP['1080p'];
  }
  return RESOLUTION_MAP[resolution];
}

export const DEFAULT_WEBCAM_SETTINGS: WebcamSettings = {
  enabled: true,
  mirror: true,
  bounds: { x: 1000, y: 520, width: 240, height: 180 },
  borderRadius: 16,
  filter: 'soften',
  cameraLayout: 'fullscreen',
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
  resolution: 'auto',
  framerate: 30,
  countdownSeconds: 3,
  audioEnabled: true,
  mode: 'whiteboard',
  continuousTeleprompter: false,
  recordFullInterface: true,
};
