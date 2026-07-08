import { useEffect, useState } from 'react';

interface CountdownProps {
  seconds: number;
  onComplete: () => void;
}

export function Countdown({ seconds, onComplete }: CountdownProps) {
  const [count, setCount] = useState(seconds);

  useEffect(() => {
    if (count <= 0) {
      onComplete();
      return;
    }

    const timer = setTimeout(() => {
      setCount(count - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [count, onComplete]);

  if (count <= 0) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50 pointer-events-none">
      <div className="text-white text-[200px] font-bold animate-pulse drop-shadow-2xl">
        {count}
      </div>
    </div>
  );
}
