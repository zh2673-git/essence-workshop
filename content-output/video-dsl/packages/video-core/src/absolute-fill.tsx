import React from 'react';

export interface AbsoluteFillProps {
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export const AbsoluteFill: React.FC<AbsoluteFillProps> = ({ style, children }) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        ...style,
      }}
    >
      {children}
    </div>
  );
};
