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
import { WorkSelector } from './components/WorkSelector';
import { CompositionRenderer } from './modules/CompositionRenderer';
import { MediaCapture } from './modules/MediaCapture';
import { WebcamModule } from './modules/WebcamModule';
import { ScreenCaptureModule } from './modules/ScreenCaptureModule';
import { HandGestureModule } from './modules/HandGestureModule';
import { CursorEffects } from './modules/CursorEffects';
import { RecordingController } from './modules/RecordingController';
import { sceneManager } from './modules/SceneManager';
import { useAppStore } from './store/useAppStore';
import { getResolutionDimensions, getCameraLayoutDimensions } from './types';
import { getSupportedMimeType } from './utils/mediaUtils';
import type { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types/types';
import type { WhiteboardProject } from './types';

function App() {
  const {
    status,
    webcam,
    cursor,
    gesture,
    recording,
    setStatus,
    setElapsedTime,
    setRecordedBlob,
    setRecordedUrl,
    setError,
    updateWebcamSettings,
    updateGestureSettings,
  } = useAppStore();

  const previewCanvasRef = useRef<HTMLCanvasElement>(null);
  const recordingCanvasRef = useRef<HTMLCanvasElement>(null);
  const webcamCanvasRef = useRef<HTMLCanvasElement>(null);
  const cursorCanvasRef = useRef<HTMLCanvasElement>(null);
  const hiddenVideoRef = useRef<HTMLVideoElement>(null);
  const screenVideoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const recordingAreaRef = useRef<HTMLDivElement>(null);

  const previewRendererRef = useRef<CompositionRenderer | null>(null);
  const recordingRendererRef = useRef<CompositionRenderer | null>(null);
  const mediaCaptureRef = useRef<MediaCapture | null>(null);
  const webcamModuleRef = useRef<WebcamModule | null>(null);
  const screenCaptureRef = useRef<ScreenCaptureModule | null>(null);
  const handGestureModuleRef = useRef<HandGestureModule | null>(null);
  const cursorEffectsRef = useRef<CursorEffects | null>(null);
  const recordingControllerRef = useRef<RecordingController | null>(null);
  const fullUIStreamRef = useRef<MediaStream | null>(null);

  const [countdownActive, setCountdownActive] = useState(false);
  const [renderScale, setRenderScale] = useState(1);
  const [autoLoaded, setAutoLoaded] = useState(false);
  const [selectedWorkId, setSelectedWorkId] = useState<string | null>(null);
  const [showWorkSelector, setShowWorkSelector] = useState(false);
  const [gestureStatus, setGestureStatus] = useState<{ status: string; message: string }>({
    status: 'idle',
    message: '',
  });
  // 录制期间锁定的画布分辨率。MediaRecorder 的 captureStream 无法处理画布尺寸动态变化，
  // 否则会导致黑屏。录制开始时锁定，结束时释放。
  const [lockedResolution, setLockedResolution] = useState<{ width: number; height: number } | null>(null);
  const whiteboardCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const excalidrawAPIRef = useRef<ExcalidrawImperativeAPI | null>(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const workParam = urlParams.get('work');
    if (workParam) {
      setSelectedWorkId(workParam);
      setShowWorkSelector(false);
    }
  }, []);

  const loadWorkProject = useCallback((api: ExcalidrawImperativeAPI, workId: string) => {
    fetch(`/api/works/${encodeURIComponent(workId)}`)
      .then(res => {
        if (res.ok) return res.json();
        throw new Error('Failed to load work');
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
      .catch((err) => {
        setError(err instanceof Error ? err.message : '加载作品失败');
      });
  }, [setError]);

  const handleExcalidrawReady = useCallback((api: ExcalidrawImperativeAPI | null) => {
    excalidrawAPIRef.current = api;
    if (api && !autoLoaded && selectedWorkId) {
      loadWorkProject(api, selectedWorkId);
    }
  }, [autoLoaded, selectedWorkId, loadWorkProject]);

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
        const state = useAppStore.getState();
        if (e.key === ' ' && state.recording.continuousTeleprompter) {
          // 连续提词器模式下，空格由 TeleprompterPanel 处理滚动暂停/继续
          return;
        }
        const currentIdx = state.currentSceneIndex;
        const total = sceneManager.getTotalScenes();
        if (currentIdx < total - 1) {
          if (sceneManager.goToScene(currentIdx + 1)) {
            state.setCurrentSceneIndex(currentIdx + 1);
            const project = state.whiteboardProject;
            if (project) {
              state.setSceneTeleprompter(project.scenes[currentIdx + 1]);
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

    const baseResolution = getResolutionDimensions(recording.resolution);
    const resolution = recording.mode === 'camera'
      ? getCameraLayoutDimensions(webcam.cameraLayout, baseResolution.width, baseResolution.height)
      : baseResolution;

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

    const captureResolution = { width: baseResolution.width, height: baseResolution.height };
    mediaCaptureRef.current?.setCaptureResolution(captureResolution.width, captureResolution.height);
    webcamModuleRef.current?.setTargetResolution(captureResolution.width, captureResolution.height);

    const mediaCapture = new MediaCapture(hiddenVideoRef.current);
    mediaCaptureRef.current = mediaCapture;

    const screenCapture = new ScreenCaptureModule(screenVideoRef.current || hiddenVideoRef.current);
    screenCaptureRef.current = screenCapture;

    const handGestureModule = new HandGestureModule({
      videoElement: hiddenVideoRef.current,
      mirror: gesture.mirror,
      onMove: (x, y) => {
        cursorEffectsRef.current?.setGestureTarget(x, y);
      },
      onStatusChange: (status, message) => {
        setGestureStatus({ status, message: message || '' });
      },
    });
    handGestureModuleRef.current = handGestureModule;

    const webcamModule = new WebcamModule(webcamCanvasRef.current, hiddenVideoRef.current);
    webcamModule.setGestureMode(gesture.enabled, handGestureModule);
    webcamModuleRef.current = webcamModule;

    return () => {
      previewRenderer.destroy();
      recordingRenderer.destroy();
      mediaCapture.destroy();
      webcamModule.destroy();
      screenCapture.destroy();
      handGestureModule.destroy();
      recordingControllerRef.current?.destroy();
      cursorEffectsRef.current?.destroy();
    };
  }, []);

  useEffect(() => {
    if (!previewRendererRef.current || !recordingRendererRef.current || !webcamModuleRef.current) return;

    const baseResolution = getResolutionDimensions(recording.resolution);
    const dynamicResolution = recording.mode === 'camera'
      ? getCameraLayoutDimensions(webcam.cameraLayout, baseResolution.width, baseResolution.height)
      : baseResolution;
    const isLocked = lockedResolution !== null;

    // 录制中不改变任何画布尺寸，否则 captureStream 会输出黑屏
    if (!isLocked) {
      previewRendererRef.current.setResolution(dynamicResolution.width, dynamicResolution.height);
      recordingRendererRef.current.setResolution(dynamicResolution.width, dynamicResolution.height);
      mediaCaptureRef.current?.setCaptureResolution(baseResolution.width, baseResolution.height);
      screenCaptureRef.current?.setCaptureResolution(baseResolution.width, baseResolution.height);
      webcamModuleRef.current?.setTargetResolution(baseResolution.width, baseResolution.height);
    }

    webcamModuleRef.current.setBounds(webcam.bounds);

    const isCameraMode = recording.mode === 'camera';

    previewRendererRef.current.setWebcamBounds(webcam.bounds);
    previewRendererRef.current.setWebcamMirror(webcam.mirror);
    previewRendererRef.current.setWebcamBorderRadius(webcam.borderRadius);
    previewRendererRef.current.setWebcamEnabled(webcam.enabled);
    previewRendererRef.current.setCursorEnabled(cursor.enabled && !isCameraMode);

    recordingRendererRef.current.setWebcamBounds(webcam.bounds);
    recordingRendererRef.current.setWebcamMirror(webcam.mirror);
    recordingRendererRef.current.setWebcamBorderRadius(webcam.borderRadius);
    recordingRendererRef.current.setWebcamEnabled(webcam.enabled);
    recordingRendererRef.current.setCursorEnabled(cursor.enabled && !isCameraMode);

    webcamModuleRef.current.setMirror(webcam.mirror);
    webcamModuleRef.current.setFilter(webcam.filter);

    if (cursorEffectsRef.current) {
      const isGesture = gesture.enabled;
      cursorEffectsRef.current.setStyle({
        color: isGesture ? gesture.color : cursor.color,
        size: isGesture ? gesture.size : cursor.size,
        showClickEffect: cursor.showClickEffect,
        clickEffectColor: cursor.clickEffectColor,
        icon: isGesture ? gesture.icon : undefined,
      });
      if (!isLocked) {
        cursorEffectsRef.current.setSize(dynamicResolution.width, dynamicResolution.height);
      }
      cursorEffectsRef.current.setGestureMode(isGesture);
    }
  }, [webcam, cursor, gesture, recording.resolution, recording.mode, lockedResolution]);

  useEffect(() => {
    const updateScale = () => {
      if (!containerRef.current) return;
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      const baseResolution = getResolutionDimensions(recording.resolution);
      const dynamicResolution = recording.mode === 'camera'
        ? getCameraLayoutDimensions(webcam.cameraLayout, baseResolution.width, baseResolution.height)
        : baseResolution;
      const res = lockedResolution ?? dynamicResolution;
      const scaleX = containerWidth / res.width;
      const scaleY = containerHeight / res.height;
      setRenderScale(Math.min(scaleX, scaleY, 1));
    };

    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, [recording.resolution, recording.mode, webcam.cameraLayout, lockedResolution]);

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
      const baseResolution = getResolutionDimensions(recording.resolution);
      const resolution = recording.mode === 'camera'
        ? getCameraLayoutDimensions(webcam.cameraLayout, baseResolution.width, baseResolution.height)
        : baseResolution;
      cursorEffects.setSize(resolution.width, resolution.height);
      cursorEffects.setStyle({
        color: cursor.color,
        size: cursor.size,
        showClickEffect: cursor.showClickEffect,
        clickEffectColor: cursor.clickEffectColor,
      });
      cursorEffects.setGestureMode(gesture.enabled);
      cursorEffects.start();
    }
  }, [cursor, recording.resolution]);

  // gesture 启用时强制打开摄像头；关闭摄像头时同步关闭手势
  useEffect(() => {
    if (gesture.enabled && !webcam.enabled) {
      updateWebcamSettings({ enabled: true });
    }
  }, [gesture.enabled, webcam.enabled, updateWebcamSettings]);

  useEffect(() => {
    if (!webcam.enabled && gesture.enabled) {
      updateGestureSettings({ enabled: false });
    }
  }, [webcam.enabled, gesture.enabled, updateGestureSettings]);

  useEffect(() => {
    handGestureModuleRef.current?.setMirror(gesture.mirror);
    cursorEffectsRef.current?.setGestureMode(gesture.enabled);
    webcamModuleRef.current?.setGestureMode(gesture.enabled, handGestureModuleRef.current);
  }, [gesture.mirror, gesture.enabled]);

  useEffect(() => {
    const isCameraMode = recording.mode === 'camera';
    previewRendererRef.current?.setWebcamCameraMode(isCameraMode);
    previewRendererRef.current?.setWebcamCameraLayout(webcam.cameraLayout);
    recordingRendererRef.current?.setWebcamCameraMode(isCameraMode);
    recordingRendererRef.current?.setWebcamCameraLayout(webcam.cameraLayout);

    const isScreenMode = recording.mode === 'screen';
    if (isScreenMode && screenCaptureRef.current) {
      screenCaptureRef.current.requestScreen().then((granted) => {
        if (granted) {
          screenCaptureRef.current?.start();
          previewRendererRef.current?.setSources(
            whiteboardCanvasRef.current,
            webcamCanvasRef.current,
            cursorCanvasRef.current,
            screenCaptureRef.current?.getVideoElement() || null
          );
          recordingRendererRef.current?.setSources(
            whiteboardCanvasRef.current,
            webcamCanvasRef.current,
            cursorCanvasRef.current,
            screenCaptureRef.current?.getVideoElement() || null
          );
        } else {
          setError('屏幕捕获被拒绝，已切换到白板讲解模式');
          useAppStore.getState().updateRecordingSettings({ mode: 'whiteboard' });
        }
      });
    } else if (!isScreenMode && screenCaptureRef.current) {
      screenCaptureRef.current.stop();
      previewRendererRef.current?.setSources(
        whiteboardCanvasRef.current,
        webcamCanvasRef.current,
        cursorCanvasRef.current,
        null
      );
      recordingRendererRef.current?.setSources(
        whiteboardCanvasRef.current,
        webcamCanvasRef.current,
        cursorCanvasRef.current,
        null
      );
    }
  }, [recording.mode, webcam.cameraLayout]);

  useEffect(() => {
    if ((recording.mode === 'camera' || recording.mode === 'screen') && !webcam.enabled) {
      updateWebcamSettings({ enabled: true });
    }
  }, [recording.mode, webcam.enabled, updateWebcamSettings]);

  // 录制结束后释放分辨率锁，让画布恢复跟随设置动态调整
  useEffect(() => {
    if (status === 'idle' || status === 'done' || status === 'error') {
      setLockedResolution(null);
    }
  }, [status]);

  useEffect(() => {
    const state = useAppStore.getState();
    const project = state.whiteboardProject;
    if (!project) return;
    const currentIdx = state.currentSceneIndex;
    if (recording.continuousTeleprompter) {
      const fullText = project.scenes
        .map((s, i) => `【${s.title || `第${i + 1}段`}】\n${s.teleprompter_script}`)
        .join('\n\n');
      state.updateTeleprompterSettings({ text: fullText });
    } else {
      state.updateTeleprompterSettings({ text: project.scenes[currentIdx]?.teleprompter_script || '' });
    }
  }, [recording.continuousTeleprompter]);

  useEffect(() => {
    if (webcam.enabled && mediaCaptureRef.current && webcamModuleRef.current) {
      mediaCaptureRef.current.requestPermissions(true, false).then(({ videoGranted }) => {
        if (videoGranted) {
          webcamModuleRef.current?.start();
          if (gesture.enabled) {
            handGestureModuleRef.current?.start();
          }
        }
      });
    } else if (!webcam.enabled && mediaCaptureRef.current) {
      webcamModuleRef.current?.stop();
      handGestureModuleRef.current?.stop();
      mediaCaptureRef.current.stopWebcam();
    }
  }, [webcam.enabled, gesture.enabled]);

  useEffect(() => {
    const mimeType = getSupportedMimeType();
    if (!mimeType) {
      setError('您的浏览器不支持视频录制功能，请使用Chrome或Edge浏览器');
    }
  }, [setError]);

  const handleStartRecording = useCallback(async () => {
    if (!recordingRendererRef.current || !mediaCaptureRef.current) return;

    // 锁定录制分辨率：录制期间画布尺寸不可变更，否则 captureStream 会输出黑屏
    const baseRes = getResolutionDimensions(recording.resolution);
    setLockedResolution(
      recording.mode === 'camera'
        ? getCameraLayoutDimensions(webcam.cameraLayout, baseRes.width, baseRes.height)
        : baseRes
    );

    try {
      if (recording.mode === 'whiteboard' && recording.recordFullInterface) {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: {
            displaySurface: 'browser',
            preferCurrentTab: true,
            selfBrowserSurface: 'include',
          } as MediaTrackConstraints,
          audio: false,
        });
        fullUIStreamRef.current = stream;
        if (screenVideoRef.current) {
          screenVideoRef.current.srcObject = stream;
          screenVideoRef.current.play().catch(() => {});
        }
        stream.getVideoTracks().forEach((track) => {
          track.onended = () => {
            fullUIStreamRef.current = null;
            if (screenVideoRef.current) {
              screenVideoRef.current.srcObject = null;
            }
          };
        });
      }

      let permissionResult = { videoGranted: false, audioGranted: false };
      if (recording.audioEnabled) {
        permissionResult = await mediaCaptureRef.current.requestPermissions(webcam.enabled, true);
      } else if (webcam.enabled) {
        permissionResult = await mediaCaptureRef.current.requestPermissions(true, false);
      }

      const needVideo = recording.mode === 'camera' || (recording.mode === 'screen' && !recording.recordFullInterface) || webcam.enabled;
      const needAudio = recording.audioEnabled;
      if ((needVideo && !permissionResult.videoGranted) || (needAudio && !permissionResult.audioGranted)) {
        if (fullUIStreamRef.current) {
          fullUIStreamRef.current.getTracks().forEach((t) => t.stop());
          fullUIStreamRef.current = null;
        }
        setError('需要摄像头/麦克风权限才能继续录制');
        return;
      }

      setCountdownActive(true);
      setStatus('countdown');
    } catch (err) {
      if (fullUIStreamRef.current) {
        fullUIStreamRef.current.getTracks().forEach((t) => t.stop());
        fullUIStreamRef.current = null;
      }
      setError(err instanceof Error ? err.message : '启动录制失败');
    }
  }, [recording.audioEnabled, recording.mode, recording.resolution, recording.recordFullInterface, webcam.enabled, webcam.cameraLayout, setStatus, setError]);

  const handleCountdownComplete = useCallback(() => {
    setCountdownActive(false);

    if (!recordingRendererRef.current || !mediaCaptureRef.current) return;

    const useFullUI = recording.mode === 'whiteboard' && recording.recordFullInterface && fullUIStreamRef.current;
    if (useFullUI) {
      recordingRendererRef.current.stop();
    } else {
      recordingRendererRef.current.start();
    }

    const controller = new RecordingController(
      {
        getVideoStream: () => {
          if (useFullUI) {
            return fullUIStreamRef.current!;
          }
          return recordingRendererRef.current!.getCanvas().captureStream(recording.framerate);
        },
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
      if (screenVideoRef.current) {
        screenVideoRef.current.srcObject = null;
      }
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
    if (fullUIStreamRef.current) {
      fullUIStreamRef.current.getTracks().forEach((t) => t.stop());
      fullUIStreamRef.current = null;
    }
    if (screenVideoRef.current) {
      screenVideoRef.current.srcObject = null;
    }
    recordingRendererRef.current?.start();
    if (useAppStore.getState().recordedUrl) {
      URL.revokeObjectURL(useAppStore.getState().recordedUrl!);
    }
    setRecordedBlob(null);
    setRecordedUrl(null);
    setElapsedTime(0);
    setStatus('idle');
    setError(null);
  }, [setRecordedBlob, setRecordedUrl, setElapsedTime, setStatus, setError]);

  const baseResolution = getResolutionDimensions(recording.resolution);
  const dynamicResolution = recording.mode === 'camera'
    ? getCameraLayoutDimensions(webcam.cameraLayout, baseResolution.width, baseResolution.height)
    : baseResolution;
  // 录制中使用锁定的分辨率，保证画布尺寸不变，避免 captureStream 黑屏
  const resolution = lockedResolution ?? dynamicResolution;

  const handleSelectWork = useCallback((workId: string) => {
    setSelectedWorkId(workId);
    setShowWorkSelector(false);
    if (excalidrawAPIRef.current) {
      loadWorkProject(excalidrawAPIRef.current, workId);
    }
  }, [loadWorkProject]);

  const handleCloseWorkSelector = useCallback(() => {
    setShowWorkSelector(false);
  }, []);

  return (
    <div className="w-full h-full relative bg-gray-100 overflow-hidden">
      {showWorkSelector && <WorkSelector onSelect={handleSelectWork} onClose={handleCloseWorkSelector} />}
      <div ref={containerRef} className="absolute inset-0 flex items-center justify-center overflow-hidden">
        <div
          className="relative"
          style={{
            width: resolution.width,
            height: resolution.height,
            transform: `scale(${renderScale})`,
            transformOrigin: 'center center',
          }}
        >
          <div
            ref={recordingAreaRef}
            className="relative bg-white shadow-2xl"
            style={{
              width: resolution.width,
              height: resolution.height,
            }}
          >
          <WhiteboardBoard mode={recording.mode} onCanvasReady={handleWhiteboardCanvasReady} onExcalidrawReady={handleExcalidrawReady} />

          <canvas
            ref={recordingCanvasRef}
            style={{ display: 'none' }}
            width={resolution.width}
            height={resolution.height}
          />

          <canvas
            ref={webcamCanvasRef}
            className="hidden"
            width={resolution.width}
            height={resolution.height}
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
            <WebcamDragHandle renderScale={renderScale} />
          </div>
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
        <div className="mt-2 flex items-center gap-2">
          <button
            onClick={() => setShowWorkSelector(true)}
            className="text-xs bg-white/80 hover:bg-white text-gray-700 px-2 py-1 rounded border border-gray-200 shadow-sm transition-colors"
          >
            加载作品
          </button>
          {selectedWorkId && (
            <span className="text-xs text-gray-500">已加载: {selectedWorkId}</span>
          )}
        </div>
        {gesture.enabled && gestureStatus.message && (
          <div className="mt-2 flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${
              gestureStatus.status === 'detected' ? 'bg-green-500' :
              gestureStatus.status === 'error' ? 'bg-red-500' :
              gestureStatus.status === 'ready' ? 'bg-green-400' :
              'bg-yellow-400 animate-pulse'
            }`} />
            <span className="text-gray-600">{gestureStatus.message}</span>
          </div>
        )}
      </div>

      <video
        ref={hiddenVideoRef}
        style={{
          position: 'fixed',
          left: -9999,
          top: -9999,
          width: 1,
          height: 1,
          opacity: 0,
          pointerEvents: 'none',
        }}
        muted
        playsInline
        autoPlay
      />

      <video
        ref={screenVideoRef}
        style={{
          position: 'fixed',
          left: -9999,
          top: -9999,
          width: 1,
          height: 1,
          opacity: 0,
          pointerEvents: 'none',
        }}
        muted
        playsInline
        autoPlay
      />
    </div>
  );
}

export default App;
