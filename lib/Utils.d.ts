export { isNumeric, areArraysEqual };
/**
 * Checks if two arrays are equal to each other.
 * @param a first array
 * @param b second array
 * @param eq function that checks the equality of two array elements
 * @returns `true` if the two arrays are equal and `false` otherwise
 */
declare function areArraysEqual<T>(a: T[], b: T[], eq?: (a: T, b: T) => boolean): boolean;
declare function isNumeric(value: any): boolean;
