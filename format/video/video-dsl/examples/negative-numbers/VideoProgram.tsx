import React from 'react';
import {
  Composition,
  Sequence,
  AbsoluteFill,
  useSequenceTime,
  interpolate,
  FadeIn,
  FlyIn,
} from '@essence/video-core';

const TitleScene: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <FadeIn startFrame={0} endFrame={30}>
        <FlyIn direction="bottom" distance={120} startFrame={0} endFrame={40}>
          <div
            style={{
              color: '#fff',
              fontSize: 90,
              fontWeight: 'bold',
              textAlign: 'center',
              fontFamily: 'system-ui, sans-serif',
            }}
          >
            负数是什么？
          </div>
        </FlyIn>
      </FadeIn>
      <FadeIn startFrame={20} endFrame={50}>
        <div
          style={{
            color: '#94a3b8',
            fontSize: 48,
            marginTop: 40,
            textAlign: 'center',
          }}
        >
          从生活到数学
        </div>
      </FadeIn>
    </AbsoluteFill>
  );
};

const ElevatorScene: React.FC = () => {
  const frame = useSequenceTime();
  const y = interpolate(frame, [0, 120], [0, 200]);
  const opacity = interpolate(frame, [0, 20], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: '#1a1a2e',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <FadeIn startFrame={0} endFrame={20}>
        <div
          style={{
            width: 200,
            height: 300,
            border: '6px solid #fff',
            borderRadius: 20,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            transform: `translateY(${-y}px)`,
            opacity,
          }}
        >
          <div style={{ color: '#fff', fontSize: 60, fontWeight: 'bold' }}>1</div>
          <div style={{ color: '#fff', fontSize: 60, fontWeight: 'bold' }}>0</div>
          <div style={{ color: '#f43f5e', fontSize: 60, fontWeight: 'bold' }}>-1</div>
        </div>
      </FadeIn>
      <FadeIn startFrame={40} endFrame={70}>
        <div
          style={{
            color: '#fff',
            fontSize: 60,
            marginTop: 80,
            textAlign: 'center',
          }}
        >
          地下一层 = -1
        </div>
      </FadeIn>
    </AbsoluteFill>
  );
};

export const VideoProgram: React.FC = () => {
  return (
    <Composition
      id="NegativeNumbers"
      component={() => (
        <>
          <Sequence from={0} durationInFrames={90}>
            <TitleScene />
          </Sequence>
          <Sequence from={90} durationInFrames={180}>
            <ElevatorScene />
          </Sequence>
        </>
      )}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={270}
    />
  );
};
