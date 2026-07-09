import React from 'react';
import { useCurrentFrame, interpolate } from '../index.js';

export interface CompareItem {
  label: string;
  value: string;
  color?: string;
}

export interface CompareProps {
  left: CompareItem;
  right: CompareItem;
  startFrame?: number;
  endFrame?: number;
  style?: React.CSSProperties;
}

export const Compare: React.FC<CompareProps> = ({
  left,
  right,
  startFrame = 0,
  endFrame = 60,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [startFrame, endFrame], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', padding: 80, ...style }}>
      <div style={{ textAlign: 'center', opacity: progress, transform: `translateX(${-100 * (1 - progress)}px)` }}>
        <div style={{ fontSize: 48, color: left.color ?? '#f43f5e', fontWeight: 'bold' }}>{left.label}</div>
        <div style={{ fontSize: 80, color: '#fff', fontWeight: 'bold', marginTop: 24 }}>{left.value}</div>
      </div>
      <div style={{ fontSize: 72, color: '#64748b', fontWeight: 'bold', opacity: progress }}>VS</div>
      <div style={{ textAlign: 'center', opacity: progress, transform: `translateX(${100 * (1 - progress)}px)` }}>
        <div style={{ fontSize: 48, color: right.color ?? '#38bdf8', fontWeight: 'bold' }}>{right.label}</div>
        <div style={{ fontSize: 80, color: '#fff', fontWeight: 'bold', marginTop: 24 }}>{right.value}</div>
      </div>
    </div>
  );
};
