import { scaleLinear } from 'd3-scale';
import { format } from 'd3-format';
import { bisectRight, rollup, range } from 'd3-array';
import type {
  FeatureInfo,
  ICELevel,
  OrderedOneWayPD,
  UnorderedOneWayPD,
} from './types';
import type { ScaleLinear } from 'd3-scale';
export {
  scaleCanvas,
  defaultFormat,
  getYScale,
  categoricalColors,
  getHighlightedBins,
};

// Adapted from https://www.html5rocks.com/en/tutorials/canvas/hidpi/
function scaleCanvas(
  canvas: HTMLCanvasElement,
  context: CanvasRenderingContext2D,
  width: number,
  height: number
): void {
  // assume the device pixel ratio is 1 if the browser doesn't specify it
  const devicePixelRatio = window.devicePixelRatio || 1;

  // set the 'real' canvas size to the higher width/height
  canvas.width = width * devicePixelRatio;
  canvas.height = height * devicePixelRatio;

  // ...then scale it back down with CSS
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';

  // scale the drawing context so everything will work at the higher ratio
  context.scale(devicePixelRatio, devicePixelRatio);
}

function defaultFormat(x: number): string {
  /* [0, 1] is a common range for predictions and features.
  With SI suffixes, 0.5 becomes 500m. I'd rather it just be 0.5. */

  if ((x >= 0.001 && x <= 1) || (x >= -1 && x <= 0.001)) {
    return format('.3~f')(x);
  } else {
    return format('~s')(x);
  }
}

function getYScale(
  pdp: OrderedOneWayPD | UnorderedOneWayPD,
  height: number,
  facetHeight: number,
  iceLevel: ICELevel,
  scaleLocally: boolean,
  iceLineExtent: [number, number],
  iceClusterCenterExtent: [number, number],
  iceClusterBandExtent: [number, number],
  iceClusterLineExtent: [number, number],
  margin: { top: number; right: number; bottom: number; left: number }
): ScaleLinear<number, number> {
  if (scaleLocally) {
    if (iceLevel === 'lines') {
      return scaleLinear()
        .domain([pdp.ice.ice_min, pdp.ice.ice_max])
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-centers') {
      return scaleLinear()
        .domain([pdp.ice.centered_mean_min, pdp.ice.centered_mean_max])
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-bands') {
      return scaleLinear()
        .domain([pdp.ice.p10_min, pdp.ice.p90_max])
        .nice()
        .range([facetHeight - margin.bottom, margin.top]);
    } else {
      return scaleLinear()
        .domain([pdp.ice.centered_ice_min, pdp.ice.centered_ice_max])
        .nice()
        .range([facetHeight - margin.bottom, margin.top]);
    }
  } else {
    if (iceLevel === 'lines') {
      return scaleLinear()
        .domain(iceLineExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-centers') {
      return scaleLinear()
        .domain(iceClusterCenterExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-bands') {
      return scaleLinear()
        .domain(iceClusterBandExtent)
        .nice()
        .range([facetHeight - margin.bottom, margin.top]);
    } else {
      return scaleLinear()
        .domain(iceClusterLineExtent)
        .nice()
        .range([facetHeight - margin.bottom, margin.top]);
    }
  }
}

// TODO: should this function be in a different file?
function getHighlightedBins(
  info: FeatureInfo,
  values: number[],
  idx: number[]
): {
  bins: number[];
  counts: number[];
} {
  const highlightedValues = idx.map((i) => values[i]);

  if (info.kind === 'categorical') {
    const highlightedCounts = rollup(
      highlightedValues,
      (g) => g.length,
      (d) => d
    );

    const counts = info.distribution.bins.map(
      (b) => highlightedCounts.get(b) ?? 0
    );

    return {
      bins: info.distribution.bins,
      counts,
    };
  } else {
    const highlightedCounts = rollup(
      highlightedValues,
      (g) => g.length,
      (d) =>
        bisectRight(
          info.distribution.bins,
          d,
          0,
          info.distribution.bins.length - 1
        ) - 1
    );

    const counts = range(info.distribution.counts.length).map(
      (i) => highlightedCounts.get(i) ?? 0
    );

    return {
      bins: info.distribution.bins,
      counts,
    };
  }
}

const categoricalColors = {
  dark: [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
  ],
  medium: [
    '#5da6e6',
    '#ffb048',
    '#65d25c',
    '#ff6151',
    '#c696f0',
    '#be8377',
    '#ffa8f5',
    '#aeaeae',
    '#f1ef5a',
    '#66f1ff',
  ],
  light: [
    '#92d7ff',
    '#ffe479',
    '#9aff8c',
    '#ff967e',
    '#fac7ff',
    '#f2b3a6',
    '#ffdcff',
    '#e0e0e0',
    '#ffff8d',
    '#9fffff',
  ],
};
