import * as assert from 'uvu/assert';
import { test } from 'uvu';
import { getHeatmapDiffs } from '../src/vis-utils';

test('getHeatmapDiffs smaller difference at end', () => {
  const actual = getHeatmapDiffs([0, 2, 4, 5]);
  const expected = new Map([
    [0, { before: 1, after: 1 }],
    [2, { before: 1, after: 1 }],
    [4, { before: 1, after: 0.5 }],
    [5, { before: 0.5, after: 0.5 }],
  ]);
  assert.equal(actual, expected);
});

test('getHeatmapDiffs smaller difference at beginning and end', () => {
  const actual = getHeatmapDiffs([1, 2, 4, 5]);
  const expected = new Map([
    [1, { before: 0.5, after: 0.5 }],
    [2, { before: 0.5, after: 1 }],
    [4, { before: 1, after: 0.5 }],
    [5, { before: 0.5, after: 0.5 }],
  ]);
  assert.equal(actual, expected);
});

test('getHeatmapDiffs equal differences', () => {
  const actual = getHeatmapDiffs([0, 5, 10, 15]);
  const expected = new Map([
    [0, { before: 2.5, after: 2.5 }],
    [5, { before: 2.5, after: 2.5 }],
    [10, { before: 2.5, after: 2.5 }],
    [15, { before: 2.5, after: 2.5 }],
  ]);
  assert.equal(actual, expected);
});

test.run();
