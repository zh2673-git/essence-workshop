import React from 'react';
import type { CompositionConfig, TimelineContextValue } from './types.js';

export const TimelineContext = React.createContext<TimelineContextValue | null>(null);

export function useTimelineContext(): TimelineContextValue {
  const ctx = React.useContext(TimelineContext);
  if (!ctx) {
    throw new Error('useCurrentFrame/useVideoConfig must be used inside a Composition');
  }
  return ctx;
}

export function useCurrentFrame(): number {
  const ctx = React.useContext(TimelineContext);
  if (!ctx) {
    // Renderer injects global subscription when running in headless browser.
    if (typeof window !== 'undefined' && (window as any).__essence_currentFrame !== undefined) {
      const [frame, setFrame] = React.useState<number>((window as any).__essence_currentFrame ?? 0);
      React.useEffect(() => {
        const win = window as any;
        if (!win.__essence_subscribe) return;
        return win.__essence_subscribe(setFrame);
      }, []);
      return frame;
    }
    throw new Error('useCurrentFrame must be used inside a Composition');
  }
  return ctx.currentFrame;
}

export function useVideoConfig(): CompositionConfig {
  const ctx = useTimelineContext();
  return ctx.composition;
}

export const TimelineProvider: React.FC<{
  value: TimelineContextValue;
  children: React.ReactNode;
}> = ({ value, children }) => {
  return <TimelineContext.Provider value={value}>{children}</TimelineContext.Provider>;
};
