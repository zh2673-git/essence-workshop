import React from 'react';
import { useCurrentFrame, interpolate } from '../index.js';

export interface TimelineItem {
  time: string;
  title: string;
  description?: string;
}

export interface TimelineProps {
  items: TimelineItem[];
  startFrame?: number;
  revealFrames?: number;
  style?: React.CSSProperties;
}

export const Timeline: React.FC<TimelineProps> = ({
  items,
  startFrame = 0,
  revealFrames = 30,
  style,
}) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 40, padding: 60, ...style }}>
      {items.map((item, index) => {
        const itemStart = startFrame + index * revealFrames;
        const itemEnd = itemStart + revealFrames;
        const opacity = interpolate(frame, [itemStart, itemEnd], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const x = interpolate(frame, [itemStart, itemEnd], [-50, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        return (
          <div key={index} style={{ display: 'flex', alignItems: 'flex-start', opacity, transform: `translateX(${x}px)` }}>
            <div style={{ width: 20, height: 20, borderRadius: '50%', background: '#38bdf8', marginRight: 24, marginTop: 8, flexShrink: 0 }} />
            <div>
              <div style={{ color: '#38bdf8', fontSize: 36, fontWeight: 'bold' }}>{item.time}</div>
              <div style={{ color: '#fff', fontSize: 48, fontWeight: 'bold', marginTop: 8 }}>{item.title}</div>
              {item.description && (
                <div style={{ color: '#94a3b8', fontSize: 36, marginTop: 12 }}>{item.description}</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
