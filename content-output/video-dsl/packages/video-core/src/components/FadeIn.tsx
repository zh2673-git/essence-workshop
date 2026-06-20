import React from 'react';
import { useCurrentFrame, interpolate } from '../index.js';

export interface FadeInProps {
  startFrame?: number;
  endFrame?: number;
  from?: number;
  to?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const FadeIn: React.FC<FadeInProps> = ({
  startFrame = 0,
  endFrame = 30,
  from = 0,
  to = 1,
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [startFrame, endFrame], [from, to]);
  return (
    <div style={{ opacity, ...style }}>
      {children}
    </div>
  );
};
