import { scaleLinear } from 'd3-scale';
import { format } from 'd3-format';
import { bisectRight, rollup, range, mean, zip, pairs } from 'd3-array';
import type {
  Distribution,
  FeatureInfo,
  ICELevel,
  OrderedOneWayPD,
  RaincloudData,
  UnorderedOneWayPD,
} from './types';
import type { ScaleLinear } from 'd3-scale';
import { countsToPercents, getClustering } from './utils';
import { density1d } from 'fast-kde';
export {
  scaleCanvas,
  defaultFormat,
  getYScale,
  categoricalColors,
  getHighlightedBins,
  getNiceDomain,
  highlightColor,
  getMaxPercent,
  getRaincloudData,
  getHeatmapDiffs,
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
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

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
  centeredIceLineExtent: [number, number],
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
      /*
        if all the ice lines are the same, then there are no clusters.
        in this case, use the centered ice min and max for the scale.
      */
      let min = pdp.ice.centered_ice_min;
      let max = pdp.ice.centered_ice_max;

      if (pdp.ice.num_clusters !== 1) {
        const clustering = getClustering(pdp);
        min = clustering.centered_mean_min;
        max = clustering.centered_mean_max;
      }

      return scaleLinear()
        .domain([min, max])
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else {
      // cluster-lines
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
        .domain(centeredIceLineExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else if (iceLevel === 'cluster-centers') {
      return scaleLinear()
        .domain(iceClusterCenterExtent)
        .nice()
        .range([height - margin.bottom, margin.top]);
    } else {
      // cluster-lines
      return scaleLinear()
        .domain(centeredIceLineExtent)
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
): Distribution {
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

    const percents = countsToPercents(counts);

    return {
      bins: info.distribution.bins,
      counts,
      percents,
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

    const percents = countsToPercents(counts);

    return {
      bins: info.distribution.bins,
      counts,
      percents,
    };
  }
}

function getMaxPercent(
  overall: Distribution,
  highlighted: Distribution | undefined
) {
  const maxOverall = Math.max(...overall.percents);

  if (!highlighted) {
    return maxOverall;
  }

  const maxHighlighted = Math.max(...highlighted.percents);

  return Math.max(maxOverall, maxHighlighted);
}

function getNiceDomain(x: [number, number]): [number, number] {
  const niceExtent = scaleLinear().domain(x).nice().domain();
  return [niceExtent[0], niceExtent[1]];
}

function getRaincloudData(
  values: number[],
  labels: number[] | null = null
): RaincloudData {
  const combinedValues = labels
    ? zip(values, labels).map(([value, label]) => ({ value, label }))
    : values.map((value) => ({ value, label: 0 }));

  let densities: { x: number; density: number }[] = [];

  // computing the KDE requires at least two data points
  if (values.length > 1) {
    const kde = density1d(values, { pad: 0, bins: 32 });
    densities = Array.from(kde, ({ x, y }) => ({ x, density: y }));
  }

  const meanValue = mean(values) ?? 0;

  return {
    values: combinedValues,
    densities: densities,
    mean: meanValue,
  };
}

function getHeatmapDiffs(
  values: number[]
): Map<number, { before: number; after: number }> {
  const diffs = new Map(values.map((d) => [d, { before: 0, after: 0 }]));

  pairs(values).forEach(([first, second], i) => {
    const firstDiff = diffs.get(first);
    const secondDiff = diffs.get(second);

    if (!firstDiff || !secondDiff) {
      return;
    }

    const diff = (second - first) / 2;
    firstDiff.after = diff;
    secondDiff.before = diff;

    if (i === 0) {
      firstDiff.before = diff;
    }

    if (i === values.length - 2) {
      secondDiff.after = diff;
    }
  });

  return diffs;
}

const highlightColor = '#4EBA72';

const categoricalColors = {
  light: [
    '#a6cee3',
    '#fdbf6f',
    '#b2df8a',
    '#fb9a99',
    '#cab2d6',
    '#FFB3F2',
    '#D4906D',
  ],
  medium: [
    '#67a3cb',
    '#fea13f',
    '#7abf5a',
    '#f4645d',
    '#9c76b7',
    '#fb9ada',
    '#c3744a',
  ],
  dark: [
    '#1f78b4',
    '#ff7f00',
    '#33a02c',
    '#e31a1c',
    '#6a3d9a',
    '#f781bf',
    '#B15928',
  ],
};
