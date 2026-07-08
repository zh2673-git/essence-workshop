import React from 'react';
import { useCurrentFrame } from './timeline-context.js';
import type { SequenceContextValue } from './types.js';

export const SequenceContext = React.createContext<SequenceContextValue>({
  cumulatedFrom: 0,
  parentFrom: 0,
});

export interface SequenceProps {
  from?: number;
  durationInFrames?: number;
  children: React.ReactNode;
}

export function useSequenceTime(): number {
  const parent = React.useContext(SequenceContext);
  const frame = useCurrentFrame();
  return frame - parent.cumulatedFrom;
}

export const Sequence: React.FC<SequenceProps> = ({
  from = 0,
  durationInFrames = Infinity,
  children,
}) => {
  const parent = React.useContext(SequenceContext);
  const frame = useCurrentFrame();
  const cumulatedFrom = parent.cumulatedFrom + from;
  const isActive = frame >= cumulatedFrom && frame < cumulatedFrom + durationInFrames;

  if (!isActive) return null;

  return (
    <SequenceContext.Provider value={{ cumulatedFrom, parentFrom: from }}>
      {children}
    </SequenceContext.Provider>
  );
};
