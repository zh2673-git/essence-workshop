import { interpolate } from './interpolate.js';

function assertClose(actual: number, expected: number, tol = 1e-6) {
  if (Math.abs(actual - expected) > tol) {
    throw new Error(`Expected ${expected}, got ${actual}`);
  }
}

assertClose(interpolate(0, [0, 10], [0, 100]), 0);
assertClose(interpolate(5, [0, 10], [0, 100]), 50);
assertClose(interpolate(10, [0, 10], [0, 100]), 100);
assertClose(interpolate(-5, [0, 10], [0, 100]), 0);
assertClose(interpolate(15, [0, 10], [0, 100]), 100);
assertClose(interpolate(-5, [0, 10], [0, 100], { extrapolateLeft: 'identity' }), -5);
assertClose(interpolate(5, [0, 10], [0, 100], { easing: (t) => t * t }), 25);

console.log('interpolate tests passed');
