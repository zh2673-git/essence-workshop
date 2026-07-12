import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { useAppStore } from '../store/useAppStore';

export function TeleprompterPanel() {
  const { teleprompter, updateTeleprompterSettings, whiteboardProject, recording } = useAppStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [isScrolling, setIsScrolling] = useState(false);
  const rafRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);
  const scrollPosRef = useRef<number>(0);

  const { enabled, fontSize, speed, opacity, position } = teleprompter;
  const continuous = recording.continuousTeleprompter;

  const text = useMemo(() => {
    if (continuous && whiteboardProject) {
      return whiteboardProject.scenes
        .map((scene, i) => `【${scene.title || `第${i + 1}段`}】\n${scene.teleprompter_script}`)
        .join('\n\n');
    }
    return teleprompter.text;
  }, [continuous, whiteboardProject, teleprompter.text]);

  const animate = useCallback((currentTime: number) => {
    if (!scrollRef.current || !contentRef.current) return;

    if (lastTimeRef.current === 0) {
      lastTimeRef.current = currentTime;
    }

    const deltaTime = currentTime - lastTimeRef.current;
    lastTimeRef.current = currentTime;

    scrollPosRef.current += (speed * deltaTime) / 1000;
    scrollRef.current.scrollTop = scrollPosRef.current;

    const isAtBottom =
      scrollRef.current.scrollTop + scrollRef.current.clientHeight >=
      contentRef.current.scrollHeight - 10;

    if (isAtBottom) {
      setIsScrolling(false);
      return;
    }

    rafRef.current = requestAnimationFrame(animate);
  }, [speed]);

  const startScroll = useCallback(() => {
    if (!enabled) return;
    setIsScrolling(true);
    lastTimeRef.current = 0;
    rafRef.current = requestAnimationFrame(animate);
  }, [enabled, animate]);

  const pauseScroll = useCallback(() => {
    setIsScrolling(false);
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  const toggleScroll = useCallback(() => {
    if (isScrolling) {
      pauseScroll();
    } else {
      startScroll();
    }
  }, [isScrolling, pauseScroll, startScroll]);

  const resetScroll = useCallback(() => {
    pauseScroll();
    scrollPosRef.current = 0;
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [pauseScroll]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!enabled) return;
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        toggleScroll();
      } else if (e.code === 'ArrowUp') {
        e.preventDefault();
        updateTeleprompterSettings({ speed: Math.max(20, speed - 10) });
      } else if (e.code === 'ArrowDown') {
        e.preventDefault();
        updateTeleprompterSettings({ speed: Math.min(200, speed + 10) });
      } else if (e.code === 'BracketLeft') {
        e.preventDefault();
        updateTeleprompterSettings({ fontSize: Math.max(16, fontSize - 2) });
      } else if (e.code === 'BracketRight') {
        e.preventDefault();
        updateTeleprompterSettings({ fontSize: Math.min(48, fontSize + 2) });
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, toggleScroll, speed, fontSize, updateTeleprompterSettings]);

  useEffect(() => {
    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, []);

  useEffect(() => {
    resetScroll();
  }, [text, resetScroll]);

  if (!enabled) return null;

  const positionClasses: Record<string, string> = {
    top: 'top-20 left-1/2 -translate-x-1/2 w-[600px] h-[200px]',
    bottom: 'bottom-24 left-1/2 -translate-x-1/2 w-[600px] h-[200px]',
    left: 'left-4 top-1/2 -translate-y-1/2 w-[350px] h-[400px]',
    right: 'right-4 top-1/2 -translate-y-1/2 w-[350px] h-[400px]',
    center: 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[160px]',
  };

  return (
    <div
      className={`fixed ${positionClasses[position]} rounded-lg bg-black pointer-events-auto hover:pointer-events-auto z-40 transition-opacity`}
      style={{ opacity }}
      onMouseEnter={() => {
        if (scrollRef.current) scrollRef.current.style.opacity = '1';
      }}
    >
      <div className="p-2 border-b border-white/20 flex items-center justify-between text-white text-sm">
        <button
          onClick={toggleScroll}
          className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded transition-colors"
        >
          {isScrolling ? '暂停' : '播放'}
        </button>
        <button
          onClick={resetScroll}
          className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded transition-colors"
        >
          重置
        </button>
        <span className="text-white/60">空格暂停 | ↑↓调速 | []调字</span>
      </div>
      <div
        ref={scrollRef}
        className="overflow-hidden p-4 text-white leading-relaxed select-none"
        style={{
          fontSize: `${fontSize}px`,
          height: 'calc(100% - 44px)',
          lineHeight: 1.8,
        }}
      >
        {text ? (
          <div ref={contentRef} className="pb-[200px]">
            {text.split('\n').map((line, i) => (
              <p key={i} className="mb-4">
                {line}
              </p>
            ))}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-white/50 text-base text-center">
            当前场景暂无提词器文稿
            <br />
            可在设置面板粘贴讲稿，或检查白板项目是否包含 teleprompter_script
          </div>
        )}
      </div>
    </div>
  );
}
