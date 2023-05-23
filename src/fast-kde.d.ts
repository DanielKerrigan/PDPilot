declare module 'fast-kde' {
  export function density1d(
    data: number[],
    { pad: number, bins: number }
  ): Iterable<{ x: number; y: number }>;
}
