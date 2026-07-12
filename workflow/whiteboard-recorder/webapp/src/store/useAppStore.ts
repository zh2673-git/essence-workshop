import { create } from 'zustand';
import type {
  RecordingStatus,
  Bounds,
  WebcamSettings,
  CursorSettings,
  GestureSettings,
  TeleprompterSettings,
  RecordingSettings,
  WhiteboardProject,
  WhiteboardScene,
} from '../types';
import {
  DEFAULT_WEBCAM_SETTINGS,
  DEFAULT_CURSOR_SETTINGS,
  DEFAULT_GESTURE_SETTINGS,
  DEFAULT_TELEPROMPTER_SETTINGS,
  DEFAULT_RECORDING_SETTINGS,
} from '../types';
import { sceneManager } from '../modules/SceneManager';

interface AppState {
  status: RecordingStatus;
  elapsedTime: number;
  recordedBlob: Blob | null;
  recordedUrl: string | null;
  error: string | null;
  
  webcam: WebcamSettings;
  cursor: CursorSettings;
  gesture: GestureSettings;
  teleprompter: TeleprompterSettings;
  recording: RecordingSettings;

  showSettings: boolean;
  activeSettingsTab: 'webcam' | 'cursor' | 'gesture' | 'teleprompter' | 'recording' | 'scenes' | null;
  webcamDragging: boolean;
  showSceneNavigator: boolean;
  currentSceneIndex: number;
  whiteboardProject: WhiteboardProject | null;
  
  setStatus: (status: RecordingStatus) => void;
  setElapsedTime: (time: number) => void;
  setRecordedBlob: (blob: Blob | null) => void;
  setRecordedUrl: (url: string | null) => void;
  setError: (error: string | null) => void;
  
  updateWebcamSettings: (settings: Partial<WebcamSettings>) => void;
  setWebcamBounds: (bounds: Bounds) => void;
  updateCursorSettings: (settings: Partial<CursorSettings>) => void;
  updateGestureSettings: (settings: Partial<GestureSettings>) => void;
  updateTeleprompterSettings: (settings: Partial<TeleprompterSettings>) => void;
  updateRecordingSettings: (settings: Partial<RecordingSettings>) => void;
  
  toggleSettings: (tab?: AppState['activeSettingsTab']) => void;
  setWebcamDragging: (dragging: boolean) => void;
  toggleSceneNavigator: () => void;
  setCurrentSceneIndex: (index: number) => void;
  loadWhiteboardProject: (project: WhiteboardProject) => void;
  clearWhiteboardProject: () => void;
  setSceneTeleprompter: (scene: WhiteboardScene) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  status: 'idle',
  elapsedTime: 0,
  recordedBlob: null,
  recordedUrl: null,
  error: null,
  
  webcam: { ...DEFAULT_WEBCAM_SETTINGS },
  cursor: { ...DEFAULT_CURSOR_SETTINGS },
  gesture: { ...DEFAULT_GESTURE_SETTINGS },
  teleprompter: { ...DEFAULT_TELEPROMPTER_SETTINGS },
  recording: { ...DEFAULT_RECORDING_SETTINGS },
  
  showSettings: false,
  activeSettingsTab: null,
  webcamDragging: false,
  showSceneNavigator: false,
  currentSceneIndex: 0,
  whiteboardProject: null,
  
  setStatus: (status) => set({ status }),
  setElapsedTime: (elapsedTime) => set({ elapsedTime }),
  setRecordedBlob: (recordedBlob) => set({ recordedBlob }),
  setRecordedUrl: (recordedUrl) => set({ recordedUrl }),
  setError: (error) => set({ error }),
  
  updateWebcamSettings: (settings) =>
    set((state) => ({ webcam: { ...state.webcam, ...settings } })),
  setWebcamBounds: (bounds) =>
    set((state) => ({ webcam: { ...state.webcam, bounds } })),
  updateCursorSettings: (settings) =>
    set((state) => ({ cursor: { ...state.cursor, ...settings } })),
  updateGestureSettings: (settings) =>
    set((state) => ({ gesture: { ...state.gesture, ...settings } })),
  updateTeleprompterSettings: (settings) =>
    set((state) => ({ teleprompter: { ...state.teleprompter, ...settings } })),
  updateRecordingSettings: (settings) =>
    set((state) => ({ recording: { ...state.recording, ...settings } })),
  
  toggleSettings: (tab) =>
    set((state) => ({
      showSettings: tab ? true : !state.showSettings,
      activeSettingsTab: tab || (state.showSettings ? null : state.activeSettingsTab),
    })),
  setWebcamDragging: (webcamDragging) => set({ webcamDragging }),
  toggleSceneNavigator: () => set((state) => ({ showSceneNavigator: !state.showSceneNavigator })),
  setCurrentSceneIndex: (index) => set({ currentSceneIndex: index }),
  loadWhiteboardProject: (project) => set((state) => {
    const continuous = state.recording.continuousTeleprompter;
    const initialText = continuous
      ? project.scenes.map((s, i) => `【${s.title || `第${i + 1}段`}】\n${s.teleprompter_script}`).join('\n\n')
      : project.scenes[0]?.teleprompter_script || '';
    return {
      whiteboardProject: project,
      currentSceneIndex: 0,
      showSceneNavigator: true,
      teleprompter: {
        ...DEFAULT_TELEPROMPTER_SETTINGS,
        enabled: !!initialText,
        text: initialText,
      }
    };
  }),
  clearWhiteboardProject: () => {
    sceneManager.reset();
    const api = (window as any).__excalidrawAPI;
    if (api) {
      api.updateScene({ elements: [] });
    }
    set({
      whiteboardProject: null,
      currentSceneIndex: 0,
      showSceneNavigator: false,
      teleprompter: { ...DEFAULT_TELEPROMPTER_SETTINGS },
    });
  },
  setSceneTeleprompter: (scene) => set((state) => ({
    teleprompter: {
      ...state.teleprompter,
      text: state.recording.continuousTeleprompter
        ? state.teleprompter.text
        : scene.teleprompter_script,
    }
  })),
  reset: () =>
    set({
      status: 'idle',
      elapsedTime: 0,
      recordedBlob: null,
      error: null,
      webcam: { ...DEFAULT_WEBCAM_SETTINGS },
      cursor: { ...DEFAULT_CURSOR_SETTINGS },
      gesture: { ...DEFAULT_GESTURE_SETTINGS },
      teleprompter: { ...DEFAULT_TELEPROMPTER_SETTINGS },
      currentSceneIndex: 0,
    }),
}));
