import type { InterpolateOptions } from './types.js';

export function interpolate(
  input: number,
  inputRange: readonly [number, number],
  outputRange: readonly [number, number],
  options?: InterpolateOptions
): number {
  const [inMin, inMax] = inputRange;
  const [outMin, outMax] = outputRange;

  if (inMin === inMax) return outMin;

  let t = (input - inMin) / (inMax - inMin);
  const easing = options?.easing ?? ((x: number) => x);

  const leftBehavior = options?.extrapolateLeft ?? 'clamp';
  const rightBehavior = options?.extrapolateRight ?? 'clamp';

  if (t < 0) {
    if (leftBehavior === 'clamp') {
      t = 0;
    } else if (leftBehavior === 'identity') {
      return input;
    }
  }
  if (t > 1) {
    if (rightBehavior === 'clamp') {
      t = 1;
    } else if (rightBehavior === 'identity') {
      return input;
    }
  }

  return outMin + easing(t) * (outMax - outMin);
}
