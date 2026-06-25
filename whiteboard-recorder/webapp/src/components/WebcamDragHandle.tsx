import { useRef, useEffect, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Bounds } from '../types';
import { clamp } from '../utils/mathUtils';
import { RESOLUTION_MAP } from '../types';

interface WebcamDragHandleProps {
  renderScale?: number;
}

export function WebcamDragHandle({ renderScale = 1 }: WebcamDragHandleProps) {
  const {
    status,
    webcam,
    recording,
    setWebcamBounds,
    setWebcamDragging,
    webcamDragging,
  } = useAppStore();

  const dragStartRef = useRef<{
    mouseX: number;
    mouseY: number;
    boundsX: number;
    boundsY: number;
  } | null>(null);
  const isDraggingRef = useRef(false);

  const resolution = RESOLUTION_MAP[recording.resolution];
  const { bounds } = webcam;

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (status === 'recording') return;
      e.preventDefault();
      e.stopPropagation();

      isDraggingRef.current = true;
      setWebcamDragging(true);
      dragStartRef.current = {
        mouseX: e.clientX,
        mouseY: e.clientY,
        boundsX: bounds.x,
        boundsY: bounds.y,
      };
    },
    [bounds.x, bounds.y, setWebcamDragging, status]
  );

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current || !dragStartRef.current) return;

      const dx = (e.clientX - dragStartRef.current.mouseX) / renderScale;
      const dy = (e.clientY - dragStartRef.current.mouseY) / renderScale;

      const newBounds: Bounds = {
        ...bounds,
        x: clamp(
          dragStartRef.current.boundsX + dx,
          0,
          resolution.width - bounds.width
        ),
        y: clamp(
          dragStartRef.current.boundsY + dy,
          0,
          resolution.height - bounds.height
        ),
      };

      setWebcamBounds(newBounds);
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        setWebcamDragging(false);
        dragStartRef.current = null;
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [bounds, resolution, renderScale, setWebcamBounds, setWebcamDragging]);

  if (!webcam.enabled) return null;

  return (
    <div
      onMouseDown={handleMouseDown}
      className={`absolute border-2 border-dashed border-white/60 rounded-lg cursor-move z-30 ${
        webcamDragging ? 'border-blue-400 bg-blue-400/10' : 'hover:border-white/80'
      } ${status === 'recording' ? 'border-transparent cursor-default' : ''}`}
      style={{
        left: bounds.x,
        top: bounds.y,
        width: bounds.width,
        height: bounds.height,
        pointerEvents: status === 'recording' ? 'none' : 'auto',
      }}
    >
      {status !== 'recording' && (
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-black/70 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
          拖动调整位置
        </div>
      )}
    </div>
  );
}
