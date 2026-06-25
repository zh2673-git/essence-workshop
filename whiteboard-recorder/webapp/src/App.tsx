import { useEffect, useRef, useState, useCallback } from 'react';
import { WhiteboardBoard } from './components/WhiteboardBoard';
import { ControlBar } from './components/ControlBar';
import { SettingsPanel } from './components/SettingsPanel';
import { Countdown } from './components/Countdown';
import { PreviewModal } from './components/PreviewModal';
import { TeleprompterPanel } from './components/TeleprompterPanel';
import { WebcamDragHandle } from './components/WebcamDragHandle';
import { ContentImporter } from './components/ContentImporter';
import { SceneNavigator } from './components/SceneNavigator';
import { CompositionRenderer } from './modules/CompositionRenderer';
import { MediaCapture } from './modules/MediaCapture';
import { WebcamModule } from './modules/WebcamModule';
import { CursorEffects } from './modules/CursorEffects';
import { RecordingController } from './modules/RecordingController';
import { sceneManager } from './modules/SceneManager';
import { useAppStore } from './store/useAppStore';
import { RESOLUTION_MAP } from './types';
import { getSupportedMimeType } from './utils/mediaUtils';
import type { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types/types';
import type { WhiteboardProject } from './types';

function App() {
  const {
    status,
    webcam,
    cursor,
    recording,
    setStatus,
    setElapsedTime,
    setRecordedBlob,
    setRecordedUrl,
    setError,
  } = useAppStore();

  const previewCanvasRef = useRef<HTMLCanvasElement>(null);
  const recordingCanvasRef = useRef<HTMLCanvasElement>(null);
  const webcamCanvasRef = useRef<HTMLCanvasElement>(null);
  const cursorCanvasRef = useRef<HTMLCanvasElement>(null);
  const hiddenVideoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const recordingAreaRef = useRef<HTMLDivElement>(null);

  const previewRendererRef = useRef<CompositionRenderer | null>(null);
  const recordingRendererRef = useRef<CompositionRenderer | null>(null);
  const mediaCaptureRef = useRef<MediaCapture | null>(null);
  const webcamModuleRef = useRef<WebcamModule | null>(null);
  const cursorEffectsRef = useRef<CursorEffects | null>(null);
  const recordingControllerRef = useRef<RecordingController | null>(null);

  const [countdownActive, setCountdownActive] = useState(false);
  const [renderScale, setRenderScale] = useState(1);
  const [autoLoaded, setAutoLoaded] = useState(false);
  const whiteboardCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const excalidrawAPIRef = useRef<ExcalidrawImperativeAPI | null>(null);

  const handleExcalidrawReady = useCallback((api: ExcalidrawImperativeAPI | null) => {
    excalidrawAPIRef.current = api;
    if (api && !autoLoaded) {
      const urlParams = new URLSearchParams(window.location.search);
      const autoLoad = urlParams.get('autoload');
      if (autoLoad !== 'false') {
        fetch('/generated-project.json')
          .then(res => {
            if (res.ok) return res.json();
            throw new Error('No auto-load project found');
          })
          .then((project: WhiteboardProject) => {
            useAppStore.getState().loadWhiteboardProject(project);
            sceneManager.setExcalidrawAPI(api);
            sceneManager.loadProject(project);
            if (project.scenes.length > 0) {
              useAppStore.getState().setSceneTeleprompter(project.scenes[0]);
            }
            setAutoLoaded(true);
          })
          .catch(() => {
            // No auto project, that's fine
          });
      }
    }
  }, [autoLoaded]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        const currentIdx = useAppStore.getState().currentSceneIndex;
        if (currentIdx > 0) {
          if (sceneManager.goToScene(currentIdx - 1)) {
            useAppStore.getState().setCurrentSceneIndex(currentIdx - 1);
            const project = useAppStore.getState().whiteboardProject;
            if (project) {
              useAppStore.getState().setSceneTeleprompter(project.scenes[currentIdx - 1]);
            }
          }
        }
      } else if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
        e.preventDefault();
        const currentIdx = useAppStore.getState().currentSceneIndex;
        const total = sceneManager.getTotalScenes();
        if (currentIdx < total - 1) {
          if (sceneManager.goToScene(currentIdx + 1)) {
            useAppStore.getState().setCurrentSceneIndex(currentIdx + 1);
            const project = useAppStore.getState().whiteboardProject;
            if (project) {
              useAppStore.getState().setSceneTeleprompter(project.scenes[currentIdx + 1]);
            }
          }
        }
      } else if (e.key === 'Home') {
        sceneManager.goToFirstScene();
        useAppStore.getState().setCurrentSceneIndex(0);
        const project = useAppStore.getState().whiteboardProject;
        if (project && project.scenes[0]) {
          useAppStore.getState().setSceneTeleprompter(project.scenes[0]);
        }
      } else if (e.key === 'End') {
        const total = sceneManager.getTotalScenes();
        if (total > 0) {
          sceneManager.goToLastScene();
          useAppStore.getState().setCurrentSceneIndex(total - 1);
          const project = useAppStore.getState().whiteboardProject;
          if (project) {
            useAppStore.getState().setSceneTeleprompter(project.scenes[total - 1]);
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (!hiddenVideoRef.current) return;
    return () => {
    };
  }, []);

  useEffect(() => {
    if (!previewCanvasRef.current || !recordingCanvasRef.current || !webcamCanvasRef.current || !cursorCanvasRef.current || !hiddenVideoRef.current) return;

    const resolution = RESOLUTION_MAP[recording.resolution];

    const previewRenderer = new CompositionRenderer(
      previewCanvasRef.current,
      resolution.width,
      resolution.height,
      false
    );
    previewRendererRef.current = previewRenderer;

    const recordingRenderer = new CompositionRenderer(
      recordingCanvasRef.current,
      resolution.width,
      resolution.height,
      true
    );
    recordingRendererRef.current = recordingRenderer;

    const mediaCapture = new MediaCapture(hiddenVideoRef.current);
    mediaCaptureRef.current = mediaCapture;

    const webcamModule = new WebcamModule(webcamCanvasRef.current, hiddenVideoRef.current);
    webcamModuleRef.current = webcamModule;

    return () => {
      previewRenderer.destroy();
      recordingRenderer.destroy();
      mediaCapture.destroy();
      webcamModule.destroy();
      recordingControllerRef.current?.destroy();
      cursorEffectsRef.current?.destroy();
    };
  }, []);

  useEffect(() => {
    if (!previewRendererRef.current || !recordingRendererRef.current || !webcamModuleRef.current) return;

    const resolution = RESOLUTION_MAP[recording.resolution];
    previewRendererRef.current.setResolution(resolution.width, resolution.height);
    recordingRendererRef.current.setResolution(resolution.width, resolution.height);

    if (webcamCanvasRef.current) {
      webcamCanvasRef.current.width = webcam.bounds.width;
      webcamCanvasRef.current.height = webcam.bounds.height;
      webcamModuleRef.current.setBounds(webcam.bounds);
    }

    previewRendererRef.current.setWebcamBounds(webcam.bounds);
    previewRendererRef.current.setWebcamMirror(webcam.mirror);
    previewRendererRef.current.setWebcamBorderRadius(webcam.borderRadius);
    previewRendererRef.current.setWebcamEnabled(webcam.enabled);
    previewRendererRef.current.setCursorEnabled(cursor.enabled);

    recordingRendererRef.current.setWebcamBounds(webcam.bounds);
    recordingRendererRef.current.setWebcamMirror(webcam.mirror);
    recordingRendererRef.current.setWebcamBorderRadius(webcam.borderRadius);
    recordingRendererRef.current.setWebcamEnabled(webcam.enabled);
    recordingRendererRef.current.setCursorEnabled(cursor.enabled);

    webcamModuleRef.current.setMirror(webcam.mirror);
    webcamModuleRef.current.setFilter(webcam.filter);

    if (cursorEffectsRef.current) {
      cursorEffectsRef.current.setStyle({
        color: cursor.color,
        size: cursor.size,
        showClickEffect: cursor.showClickEffect,
        clickEffectColor: cursor.clickEffectColor,
      });
      cursorEffectsRef.current.setSize(resolution.width, resolution.height);
    }
  }, [webcam, cursor, recording.resolution]);

  useEffect(() => {
    const updateScale = () => {
      if (!containerRef.current) return;
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      const resolution = RESOLUTION_MAP[recording.resolution];
      const scaleX = containerWidth / resolution.width;
      const scaleY = containerHeight / resolution.height;
      setRenderScale(Math.min(scaleX, scaleY, 1));
    };

    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, [recording.resolution]);

  const handleWhiteboardCanvasReady = useCallback((canvas: HTMLCanvasElement | null) => {
    whiteboardCanvasRef.current = canvas;
    if (previewRendererRef.current && recordingRendererRef.current && webcamCanvasRef.current && cursorCanvasRef.current) {
      previewRendererRef.current.setSources(canvas, webcamCanvasRef.current, cursorCanvasRef.current);
      previewRendererRef.current.start();
      recordingRendererRef.current.setSources(canvas, webcamCanvasRef.current, cursorCanvasRef.current);
      recordingRendererRef.current.start();
    }

    if (canvas && recordingAreaRef.current && !cursorEffectsRef.current && cursorCanvasRef.current) {
      const cursorEffects = new CursorEffects(cursorCanvasRef.current, recordingAreaRef.current);
      cursorEffectsRef.current = cursorEffects;
      const resolution = RESOLUTION_MAP[recording.resolution];
      cursorEffects.setSize(resolution.width, resolution.height);
      cursorEffects.setStyle({
        color: cursor.color,
        size: cursor.size,
        showClickEffect: cursor.showClickEffect,
        clickEffectColor: cursor.clickEffectColor,
      });
      cursorEffects.start();
    }
  }, [cursor, recording.resolution]);

  useEffect(() => {
    if (webcam.enabled && mediaCaptureRef.current && webcamModuleRef.current) {
      mediaCaptureRef.current.requestPermissions(true, false).then(({ videoGranted }) => {
        if (videoGranted) {
          webcamModuleRef.current?.start();
        }
      });
    } else if (!webcam.enabled && mediaCaptureRef.current) {
      webcamModuleRef.current?.stop();
      mediaCaptureRef.current.stopWebcam();
    }
  }, [webcam.enabled]);

  useEffect(() => {
    const mimeType = getSupportedMimeType();
    if (!mimeType) {
      setError('您的浏览器不支持视频录制功能，请使用Chrome或Edge浏览器');
    }
  }, [setError]);

  const handleStartRecording = useCallback(async () => {
    if (!recordingRendererRef.current || !mediaCaptureRef.current) return;

    try {
      if (recording.audioEnabled) {
        await mediaCaptureRef.current.requestPermissions(webcam.enabled, true);
      } else if (webcam.enabled) {
        await mediaCaptureRef.current.requestPermissions(true, false);
      }

      setCountdownActive(true);
      setStatus('countdown');
    } catch (err) {
      setError(err instanceof Error ? err.message : '启动录制失败');
    }
  }, [recording.audioEnabled, webcam.enabled, setStatus, setError]);

  const handleCountdownComplete = useCallback(() => {
    setCountdownActive(false);

    if (!recordingRendererRef.current || !mediaCaptureRef.current) return;

    const controller = new RecordingController(
      {
        getCanvas: () => recordingRendererRef.current!.getCanvas(),
        getAudioStream: () => mediaCaptureRef.current!.getAudioStream(),
        onStatusChange: (status) => {
          if (status !== 'processing') {
            setStatus(status);
          }
        },
        onTimeUpdate: (time) => setElapsedTime(time),
        onError: (error) => {
          setError(error);
          setStatus('error');
        },
      },
      recording
    );

    recordingControllerRef.current = controller;

    controller.startRecording().then(() => {
      setElapsedTime(0);
    });
  }, [recording, setStatus, setElapsedTime, setError]);

  const handlePauseRecording = useCallback(() => {
    recordingControllerRef.current?.pauseRecording();
  }, []);

  const handleResumeRecording = useCallback(() => {
    recordingControllerRef.current?.resumeRecording();
  }, []);

  const handleStopRecording = useCallback(async () => {
    if (!recordingControllerRef.current) return;

    setStatus('processing');
    try {
      const blob = await recordingControllerRef.current.stopRecording();
      setRecordedBlob(blob);
      setStatus('done');
    } catch (err) {
      setError(err instanceof Error ? err.message : '录制失败');
      setStatus('error');
    }
  }, [setStatus, setRecordedBlob, setError]);

  const handleReset = useCallback(() => {
    if (recordingControllerRef.current) {
      recordingControllerRef.current.reset();
      recordingControllerRef.current.destroy();
      recordingControllerRef.current = null;
    }
    if (useAppStore.getState().recordedUrl) {
      URL.revokeObjectURL(useAppStore.getState().recordedUrl!);
    }
    setRecordedBlob(null);
    setRecordedUrl(null);
    setElapsedTime(0);
    setStatus('idle');
    setError(null);
  }, [setRecordedBlob, setRecordedUrl, setElapsedTime, setStatus, setError]);

  const resolution = RESOLUTION_MAP[recording.resolution];

  return (
    <div className="w-full h-full relative bg-gray-100 overflow-hidden">
      <div ref={containerRef} className="absolute inset-0 flex items-center justify-center">
        <div
          ref={recordingAreaRef}
          className="relative bg-white shadow-2xl"
          style={{
            width: resolution.width,
            height: resolution.height,
            transform: `scale(${renderScale})`,
            transformOrigin: 'center center',
          }}
        >
          <WhiteboardBoard onCanvasReady={handleWhiteboardCanvasReady} onExcalidrawReady={handleExcalidrawReady} />

          <canvas
            ref={recordingCanvasRef}
            style={{ display: 'none' }}
            width={resolution.width}
            height={resolution.height}
          />

          <canvas
            ref={webcamCanvasRef}
            className="hidden"
            width={webcam.bounds.width}
            height={webcam.bounds.height}
          />

          <canvas
            ref={cursorCanvasRef}
            className="hidden"
            width={resolution.width}
            height={resolution.height}
          />

          <canvas
            ref={previewCanvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none"
            style={{
              zIndex: 10,
            }}
          />

          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              zIndex: 11,
            }}
          >
            <WebcamDragHandle renderScale={1} />
          </div>
        </div>
      </div>

      {countdownActive && (
        <Countdown
          seconds={recording.countdownSeconds}
          onComplete={handleCountdownComplete}
        />
      )}

      {status !== 'countdown' && (
        <ControlBar
          onStartRecording={handleStartRecording}
          onPauseRecording={handlePauseRecording}
          onResumeRecording={handleResumeRecording}
          onStopRecording={handleStopRecording}
        />
      )}

      <SettingsPanel />
      <TeleprompterPanel />
      <SceneNavigator />

      <div className="fixed top-4 right-4 z-40 flex items-center gap-2">
        <ContentImporter />
      </div>

      {status === 'done' && <PreviewModal onReset={handleReset} />}

      {status === 'processing' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 flex items-center gap-4">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-gray-700 font-medium">正在处理视频...</span>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          {useAppStore.getState().error || '发生错误'}
        </div>
      )}

      <div className="fixed top-4 left-4 z-40">
        <h1 className="text-xl font-bold text-gray-700 flex items-center gap-2">
          <span className="text-2xl">🎨</span>
          WhiteboardCaster
        </h1>
      </div>

      <video
        ref={hiddenVideoRef}
        style={{ display: 'none' }}
        muted
        playsInline
        autoPlay
      />
    </div>
  );
}

export default App;
