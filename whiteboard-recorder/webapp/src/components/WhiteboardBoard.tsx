import { useEffect, useRef, useCallback } from 'react';
import { Excalidraw } from '@excalidraw/excalidraw';
import type { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types/types';
import { sceneManager } from '../modules/SceneManager';

interface WhiteboardBoardProps {
  onCanvasReady?: (canvas: HTMLCanvasElement | null) => void;
  onExcalidrawReady?: (api: ExcalidrawImperativeAPI | null) => void;
}

export function WhiteboardBoard({ onCanvasReady, onExcalidrawReady }: WhiteboardBoardProps) {
  const excalidrawApiRef = useRef<ExcalidrawImperativeAPI | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const findCanvas = useCallback(() => {
    if (!containerRef.current) return null;
    const canvases = containerRef.current.querySelectorAll('canvas');
    for (const canvas of Array.from(canvases)) {
      if (canvas.width > 100 && canvas.height > 100) {
        return canvas as HTMLCanvasElement;
      }
    }
    return null;
  }, []);

  useEffect(() => {
    let cancelled = false;
    const checkCanvas = () => {
      if (cancelled) return;
      const canvas = findCanvas();
      if (canvas) {
        onCanvasReady?.(canvas);
      } else {
        requestAnimationFrame(checkCanvas);
      }
    };
    const timer = setTimeout(checkCanvas, 100);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [findCanvas, onCanvasReady]);

  const handleExcalidrawAPI = useCallback((api: ExcalidrawImperativeAPI) => {
    excalidrawApiRef.current = api;
    sceneManager.setExcalidrawAPI(api);
    (window as any).__excalidrawAPI = api;
    onExcalidrawReady?.(api);
  }, [onExcalidrawReady]);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full"
      style={{ zIndex: 1 }}
    >
      <Excalidraw
        excalidrawAPI={handleExcalidrawAPI}
        initialData={{
          appState: {
            viewBackgroundColor: '#ffffff',
            gridSize: null,
          },
        }}
        theme="light"
      />
    </div>
  );
}
