import { sum } from 'd3-array';
import type { OneWayPD, Clustering } from './types';

export {
  areArraysEqual,
  atOrValue,
  clamp,
  isNumeric,
  countsToPercents,
  getClustering,
  centerIceLines,
};

/**
 * Checks if two arrays are equal to each other.
 * @param a first array
 * @param b second array
 * @param eq function that checks the equality of two array elements
 * @returns `true` if the two arrays are equal and `false` otherwise
 */
function areArraysEqual<T>(
  a: T[],
  b: T[],
  eq: (a: T, b: T) => boolean = (x: T, y: T) => x === y
): boolean {
  if (a.length !== b.length) {
    return false;
  }

  for (let i = 0; i < a.length; i++) {
    if (!eq(a[i], b[i])) {
      return false;
    }
  }

  return true;
}

/* If `a` is an array, return the value at the given `index`. Otherwise,
return `a`.*/
function atOrValue<T>(a: T[] | T, index: number): T {
  return Array.isArray(a) ? a[index] : a;
}

/* Return `value` clamped to the range given by `low` and `high`. */
function clamp(value: number, low: number, high: number): number {
  return Math.min(Math.max(value, low), high);
}

/* https://stackoverflow.com/questions/175739/built-in-way-in-javascript-to-check-if-a-string-is-a-valid-number
   return true if the passed in value is a number or a string that is number */
function isNumeric(value: any): boolean {
  return !isNaN(value) && !isNaN(parseFloat(value));
}

/**
 * Divides each number in the passed array by the sum of the array.
 * @param x array of counts
 * @returns array of percents
 */
function countsToPercents(x: number[]): number[] {
  const total = sum(x);
  return x.map((d) => d / total);
}

function getClustering(pd: OneWayPD, numClusters = -1): Clustering {
  if (numClusters === -1) {
    numClusters = pd.ice.num_clusters;
  }
  return (
    pd.ice.adjusted_clusterings[numClusters] ?? pd.ice.clusterings[numClusters]
  );
}

/**
 * Centers the ICE lines.
 * @param iceLines standard ICE lines
 * @returns centered ICE lines
 */
function centerIceLines(iceLines: number[][]): number[][] {
  return iceLines.map((line) => line.map((d) => d - line[0]));
}
