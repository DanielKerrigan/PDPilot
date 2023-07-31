import type { OneWayPD, TwoWayPD, PDSortingOption } from './types';

import { isOneWayPdArray } from './types';

import { descending, transpose, mean } from 'd3-array';
import { centerIceLines, getClustering } from './utils';

export { singlePDPSortingOptions, doublePDPSortingOptions };

function distanceRatio(
  highlightedLines: number[][],
  highlightedCenter: number[],
  pd: number[]
): number[] {
  return highlightedLines.map((highlightedLine) => {
    let distanceToHighltedCenter = 0;
    let distanceToPd = 0;
    for (let i = 0; i < highlightedLine.length; i++) {
      distanceToHighltedCenter +=
        (highlightedLine[i] - highlightedCenter[i]) ** 2;
      distanceToPd += (highlightedLine[i] - pd[i]) ** 2;
    }
    return Math.sqrt(distanceToPd) / Math.sqrt(distanceToHighltedCenter);
  });
}

const singlePDPSortingOptions: PDSortingOption[] = [
  {
    name: 'Importance',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
  {
    name: 'Cluster difference',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      function getDistance(pd: OneWayPD) {
        if (pd.ice.num_clusters === 1) {
          return -Infinity;
        }

        return getClustering(pd).cluster_distance;
      }

      return data.sort((a, b) => descending(getDistance(a), getDistance(b)));
    },
  },
  {
    name: 'Highlighted line similarity',
    forBrushing: true,
    sort: function (
      data: OneWayPD[] | TwoWayPD[],
      extra
    ): OneWayPD[] | TwoWayPD[] {
      if (
        data.length === 0 ||
        !isOneWayPdArray(data) ||
        !extra ||
        !extra.highlightedIndices ||
        extra.highlightedIndices.length <= 1 ||
        !extra.featureToIceLines
      ) {
        return data;
      }

      const indices = extra.highlightedIndices;
      const featureToIceLines = extra.featureToIceLines;

      const scores = Object.fromEntries(
        data.map((pd) => {
          const allIceLines = featureToIceLines[pd.x_feature];
          const standardIceLines = indices.map((i) => allIceLines[i]);
          const highlightedLines = centerIceLines(standardIceLines);
          const highlightedCenter = transpose<number>(highlightedLines).map(
            (points) => mean(points) ?? 0
          );

          const scores = distanceRatio(
            highlightedLines,
            highlightedCenter,
            pd.ice.centered_pdp
          );

          return [pd.x_feature, mean(scores) ?? 0];
        })
      );

      return data.sort((a, b) =>
        descending(scores[a.x_feature], scores[b.x_feature])
      );
    },
  },
  {
    name: 'Highlighted histogram difference',
    forBrushing: true,
    sort: function (
      data: OneWayPD[] | TwoWayPD[],
      extra
    ): OneWayPD[] | TwoWayPD[] {
      if (
        data.length === 0 ||
        !isOneWayPdArray(data) ||
        !extra ||
        !extra.highlightedDistributions ||
        !extra.featureInfo
      ) {
        return data;
      }

      const highlightedDistributions = extra.highlightedDistributions;
      const featureInfo = extra.featureInfo;

      const scores = Object.fromEntries(
        data.map((pd) => {
          const highlightedDistribution = highlightedDistributions.get(
            pd.x_feature
          );
          if (!highlightedDistribution) {
            return [pd.x_feature, 0];
          }

          const overall = featureInfo[pd.x_feature].distribution.percents;
          const highlighted = highlightedDistribution.percents;

          let distance = 0;

          for (let i = 0; i < overall.length; i++) {
            distance += Math.abs(highlighted[i] - overall[i]);
          }

          return [pd.x_feature, distance];
        })
      );

      return data.sort((a, b) =>
        descending(scores[a.x_feature], scores[b.x_feature])
      );
    },
  },
];

const doublePDPSortingOptions: PDSortingOption[] = [
  {
    name: 'Interaction',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.H, b.H));
    },
  },
  {
    name: 'Variance',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
];
