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
    } else if (iceLevel === 'centered-lines') {
      return scaleLinear()
        .domain([pdp.ice.centered_ice_min, pdp.ice.centered_ice_max])
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-centers') {
      return scaleLinear()
        .domain([pdp.ice.centered_mean_min, pdp.ice.centered_mean_max])
        .nice()
        .range([height - margin.bottom, margin.top]);
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
    } else if (iceLevel === 'centered-lines') {
      return scaleLinear()
        .domain(iceClusterLineExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-centers') {
      return scaleLinear()
        .domain(iceClusterCenterExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
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
  light: ['#a6cee3', '#fdbf6f', '#b2df8a', '#fb9a99', '#cab2d6'],
  medium: ['#67a3cb', '#fea13f', '#7abf5a', '#f4645d', '#9c76b7'],
  dark: ['#1f78b4', '#ff7f00', '#33a02c', '#e31a1c', '#6a3d9a'],
};
