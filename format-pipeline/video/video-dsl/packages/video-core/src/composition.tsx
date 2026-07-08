import React from 'react';
import { TimelineProvider } from './timeline-context.js';
import type { CompositionConfig } from './types.js';

export interface CompositionProps {
  id: string;
  component: React.ComponentType<any>;
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  defaultProps?: Record<string, unknown>;
}

export const Composition: React.FC<CompositionProps> = ({
  component: Component,
  width,
  height,
  fps,
  durationInFrames,
  defaultProps,
}) => {
  const config: CompositionConfig = {
    id: '',
    width,
    height,
    fps,
    durationInFrames,
  };

  const [currentFrame, setCurrentFrame] = React.useState(0);

  React.useEffect(() => {
    const win = window as any;
    if (win.__essence_subscribe) {
      return win.__essence_subscribe(setCurrentFrame);
    }
  }, []);

  return (
    <TimelineProvider value={{ currentFrame, composition: config }}>
      <div
        style={{
          position: 'relative',
          width,
          height,
          overflow: 'hidden',
          background: '#000',
        }}
      >
        <Component {...(defaultProps ?? {})} />
      </div>
    </TimelineProvider>
  );
};
