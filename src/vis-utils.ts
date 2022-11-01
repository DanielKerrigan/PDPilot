import { scaleLinear } from 'd3-scale';
import { format } from 'd3-format';
import type {
  ICELevel,
  QuantitativeSinglePDPData,
  CategoricalSinglePDPData,
} from './types';
import type { ScaleLinear } from 'd3-scale';
export { scaleCanvas, defaultFormat, getYScale, categoricalColors };

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
  pdp: QuantitativeSinglePDPData | CategoricalSinglePDPData,
  height: number,
  bandHeight: number,
  iceLevel: ICELevel,
  scaleLocally: boolean,
  nicePdpExtent: [number, number],
  niceIceMeanExtent: [number, number],
  niceIceBandExtent: [number, number],
  niceIceLineExtent: [number, number],
  margin: { top: number; right: number; bottom: number; left: number }
): ScaleLinear<number, number> {
  const globalPdp = scaleLinear()
    .domain(nicePdpExtent)
    .range([height - margin.bottom, margin.top]);

  const globalIceClusterMean = scaleLinear()
    .domain(niceIceMeanExtent)
    .range([height - margin.bottom, margin.top]);

  const globalIceBand = scaleLinear()
    .domain(niceIceBandExtent)
    .range([bandHeight, margin.top]);

  const globalIceLines = scaleLinear()
    .domain(niceIceLineExtent)
    .range([bandHeight, margin.top]);

  const localPdp = scaleLinear()
    .domain([pdp.pdp_min, pdp.pdp_max])
    .range([height - margin.bottom, margin.top]);

  const localIceClusterMean = scaleLinear()
    .domain([pdp.ice.centered_mean_min, pdp.ice.centered_mean_max])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const localIceBand = scaleLinear()
    .domain([pdp.ice.p10_min, pdp.ice.p90_max])
    .nice()
    .range([bandHeight, 0]);

  const localIceLines = scaleLinear()
    .domain([pdp.ice.centered_ice_min, pdp.ice.centered_ice_max])
    .nice()
    .range([bandHeight, 0]);

  if (scaleLocally) {
    if (iceLevel === 'none') {
      return localPdp;
    } else if (iceLevel === 'mean') {
      return localIceClusterMean;
    } else if (iceLevel === 'band') {
      return localIceBand;
    } else {
      return localIceLines;
    }
  } else {
    if (iceLevel === 'none') {
      return globalPdp;
    } else if (iceLevel === 'mean') {
      return globalIceClusterMean;
    } else if (iceLevel === 'band') {
      return globalIceBand;
    } else {
      return globalIceLines;
    }
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
