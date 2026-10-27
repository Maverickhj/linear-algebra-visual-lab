/* Pure arithmetic; usable as a classic browser script and from Node. */
(function (root) {
  'use strict';
  const defaults = Object.freeze({ ax: 2, ay: 1, bx: 1, by: 2 });
  const limits = Object.freeze({ min: -3, max: 3, step: 0.5 });
  const keys = Object.keys(defaults);

  function compute(params) {
    if (!params || keys.some(key => !Number.isFinite(params[key]) ||
      params[key] < limits.min || params[key] > limits.max ||
      !Number.isInteger(params[key] / limits.step))) {
      throw new RangeError('分量必须在 −3 到 3 之间，且为 0.5 的整数倍。');
    }
    const a = [params.ax, params.ay];
    const b = [params.bx, params.by];
    const sum = [a[0] + b[0], a[1] + b[1]];
    const zero = vector => vector.every(value => value === 0);
    return { a, b, sum, aZero: zero(a), bZero: zero(b), sumZero: zero(sum) };
  }

  const model = { defaults, limits, compute };
  root.VectorAddition = model;
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
})(typeof window === 'undefined' ? globalThis : window);
