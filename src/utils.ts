import { sum } from 'd3-array';

export { isNumeric, areArraysEqual, countsToPercents };

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
