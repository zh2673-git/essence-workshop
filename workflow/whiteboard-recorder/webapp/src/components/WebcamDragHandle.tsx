import { useRef, useEffect, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Bounds } from '../types';
import { clamp } from '../utils/mathUtils';
import { getResolutionDimensions } from '../types';

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
    boundsWidth: number;
    boundsHeight: number;
    mode: 'move' | 'resize';
  } | null>(null);
  const isDraggingRef = useRef(false);
  const isResizingRef = useRef(false);

  const resolution = getResolutionDimensions(recording.resolution);
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
        boundsWidth: bounds.width,
        boundsHeight: bounds.height,
        mode: 'move',
      };
    },
    [bounds.x, bounds.y, bounds.width, bounds.height, setWebcamDragging, status]
  );

  const handleResizeMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (status === 'recording') return;
      e.preventDefault();
      e.stopPropagation();

      isResizingRef.current = true;
      setWebcamDragging(true);
      dragStartRef.current = {
        mouseX: e.clientX,
        mouseY: e.clientY,
        boundsX: bounds.x,
        boundsY: bounds.y,
        boundsWidth: bounds.width,
        boundsHeight: bounds.height,
        mode: 'resize',
      };
    },
    [bounds.x, bounds.y, bounds.width, bounds.height, setWebcamDragging, status]
  );

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current) return;

      const dx = (e.clientX - dragStartRef.current.mouseX) / renderScale;
      const dy = (e.clientY - dragStartRef.current.mouseY) / renderScale;

      if (isDraggingRef.current) {
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
      } else if (isResizingRef.current) {
        const newWidth = clamp(dragStartRef.current.boundsWidth + dx, 120, resolution.width - bounds.x);
        const newHeight = clamp(dragStartRef.current.boundsHeight + dy, 90, resolution.height - bounds.y);
        const newBounds: Bounds = {
          ...bounds,
          width: newWidth,
          height: newHeight,
        };
        setWebcamBounds(newBounds);
      }
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current || isResizingRef.current) {
        isDraggingRef.current = false;
        isResizingRef.current = false;
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

  const borderSize = 12;

  return (
    <div
      className="absolute z-30"
      style={{
        left: bounds.x,
        top: bounds.y,
        width: bounds.width,
        height: bounds.height,
        borderRadius: webcam.borderRadius,
        pointerEvents: 'none',
      }}
    >
      <div
        onMouseDown={handleMouseDown}
        className={`absolute top-0 left-0 right-0 cursor-move pointer-events-auto group ${
          webcamDragging ? 'bg-blue-400/10' : 'hover:bg-white/5'
        } ${status === 'recording' ? 'cursor-default' : ''}`}
        style={{
          height: borderSize,
          borderTopLeftRadius: 'inherit',
          borderTopRightRadius: 'inherit',
        }}
      >
        {status !== 'recording' && (
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-black/70 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            拖动调整位置
          </div>
        )}
      </div>
      <div
        onMouseDown={handleMouseDown}
        className={`absolute bottom-0 left-0 right-0 cursor-move pointer-events-auto ${
          webcamDragging ? 'bg-blue-400/10' : 'hover:bg-white/5'
        } ${status === 'recording' ? 'cursor-default' : ''}`}
        style={{
          height: borderSize,
          borderBottomLeftRadius: 'inherit',
          borderBottomRightRadius: 'inherit',
        }}
      />
      <div
        onMouseDown={handleMouseDown}
        className={`absolute top-3 bottom-3 left-0 cursor-move pointer-events-auto ${
          webcamDragging ? 'bg-blue-400/10' : 'hover:bg-white/5'
        } ${status === 'recording' ? 'cursor-default' : ''}`}
        style={{
          width: borderSize,
          borderTopLeftRadius: 'inherit',
          borderBottomLeftRadius: 'inherit',
        }}
      />
      <div
        onMouseDown={handleMouseDown}
        className={`absolute top-3 bottom-3 right-0 cursor-move pointer-events-auto ${
          webcamDragging ? 'bg-blue-400/10' : 'hover:bg-white/5'
        } ${status === 'recording' ? 'cursor-default' : ''}`}
        style={{
          width: borderSize,
          borderTopRightRadius: 'inherit',
          borderBottomRightRadius: 'inherit',
        }}
      />
      {status !== 'recording' && (
        <div
          onMouseDown={handleResizeMouseDown}
          className="absolute -bottom-1.5 -right-1.5 w-4 h-4 bg-white border border-gray-400 rounded-full cursor-nwse-resize shadow-sm hover:bg-blue-100 pointer-events-auto"
          style={{ zIndex: 40 }}
          title="拖动调整大小"
        />
      )}
    </div>
  );
}
