'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const model = require('./model.js');
const view = require('./view.js');

test('hand-computable defaults, signed halves, and boundaries', () => {
  assert.deepEqual(model.compute(model.defaults).sum, [3, 3]);
  assert.deepEqual(model.compute({ ax: -2.5, ay: 1, bx: 0.5, by: -3 }).sum, [-2, -2]);
  assert.deepEqual(model.compute({ ax: 3, ay: -3, bx: 3, by: -3 }).sum, [6, -6]);
});

test('opposites and all-zero inputs have no directed resultant arrow', () => {
  const opposite = model.compute({ ax: 2, ay: 1, bx: -2, by: -1 });
  assert.deepEqual(opposite.sum, [0, 0]);
  assert.equal(opposite.sumZero, true);
  assert.doesNotMatch(view.svg(opposite), /data-vector="sum"/);
  assert.match(view.svg(opposite), /data-zero="sum"/);
  const zero = model.compute({ ax: 0, ay: 0, bx: 0, by: 0 });
  assert.doesNotMatch(view.svg(zero), /<line /);
  assert.equal((view.svg(zero).match(/data-zero=/g) || []).length, 3);
});

test('swapping paths preserves the endpoint without mutating input', () => {
  const params = Object.freeze({ ax: 3, ay: -2, bx: -1, by: 0.5 });
  const first = model.compute(params);
  const swapped = model.compute({ ax: -1, ay: 0.5, bx: 3, by: -2 });
  assert.deepEqual(first.sum, [2, -1.5]);
  assert.deepEqual(first.sum, swapped.sum);
});

test('invalid, non-finite, missing, and off-step values are rejected', () => {
  for (const value of [NaN, Infinity, -Infinity, -3.5, 3.5, 0.1, '', null, undefined]) {
    assert.throws(() => model.compute({ ...model.defaults, ax: value }), RangeError);
  }
  assert.throws(() => model.compute(null), RangeError);
});

test('screen coordinates preserve equal lengths and invert only y', () => {
  assert.deepEqual(view.point([0, 0]), [320, 300]);
  assert.deepEqual(view.point([1, 0]), [356, 300]);
  assert.deepEqual(view.point([0, 1]), [320, 264]);
  assert.match(view.svg(model.compute(model.defaults)), /data-vector="sum" x1="320" y1="300" x2="428" y2="192"/);
});

test('committed static SVG is exactly the default interactive drawing', () => {
  const file = fs.readFileSync(path.join(__dirname, 'figure.svg'), 'utf8');
  assert.equal(file, view.svg(model.compute(model.defaults)) + '\n');
});
