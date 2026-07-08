import React from 'react';
import { useCurrentFrame, interpolate } from '../index.js';

export interface CounterProps {
  value: number;
  startFrame?: number;
  endFrame?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  style?: React.CSSProperties;
}

export const Counter: React.FC<CounterProps> = ({
  value,
  startFrame = 0,
  endFrame = 60,
  decimals = 0,
  prefix = '',
  suffix = '',
  style,
}) => {
  const frame = useCurrentFrame();
  const current = interpolate(frame, [startFrame, endFrame], [0, value], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const formatted = current.toFixed(decimals);
  return (
    <span style={style}>
      {prefix}{formatted}{suffix}
    </span>
  );
};
