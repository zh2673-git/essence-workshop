import React from 'react';
import { useCurrentFrame, interpolate } from '../index.js';

export interface FlyInProps {
  direction?: 'left' | 'right' | 'top' | 'bottom';
  distance?: number;
  startFrame?: number;
  endFrame?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const FlyIn: React.FC<FlyInProps> = ({
  direction = 'bottom',
  distance = 200,
  startFrame = 0,
  endFrame = 30,
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, endFrame], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const transforms: Record<string, string> = {
    left: `translateX(${-distance * (1 - t)}px)`,
    right: `translateX(${distance * (1 - t)}px)`,
    top: `translateY(${-distance * (1 - t)}px)`,
    bottom: `translateY(${distance * (1 - t)}px)`,
  };

  return (
    <div style={{ transform: transforms[direction], opacity: t, ...style }}>
      {children}
    </div>
  );
};
