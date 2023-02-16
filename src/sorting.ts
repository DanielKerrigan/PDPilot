import type { OneWayPD, TwoWayPD, PDSortingOption } from './types';

import { isOneWayPdArray } from './types';

import { ascending, descending, transpose, mean, sum } from 'd3-array';

export { singlePDPSortingOptions, doublePDPSortingOptions };

function meanAbsolute(lines: number[][], center: number[]): number[] {
  return lines.map((line) => {
    // calculate distance between line and center
    let score = 0;
    for (let i = 0; i < line.length; i++) {
      score += Math.abs(line[i] - center[i]);
    }
    return score / center.length;
  });
}

function normalize(x: number[]): number[] {
  const total = sum(x);
  return x.map((a) => a / total);
}

const singlePDPSortingOptions: PDSortingOption[] = [
  {
    name: 'variance',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
  {
    name: 'cluster difference',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) =>
        descending(a.ice.cluster_distance, b.ice.cluster_distance)
      );
    },
  },
  {
    name: 'complexity',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      data.sort((a, b) => {
        if (!a.ordered) {
          return 1;
        } else if (!b.ordered) {
          return -1;
        }

        if (a.knots_good_fit === b.knots_good_fit) {
          return descending(a.nrmse_good_fit, b.nrmse_good_fit);
        } else {
          return descending(a.knots_good_fit, b.knots_good_fit);
        }
      });

      return data;
    },
  },
  {
    name: 'highlighted similarity',
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
        extra.highlightedIndices.length <= 1
      ) {
        return data;
      }

      const indices = extra.highlightedIndices;

      const scores = Object.fromEntries(
        data.map((pd) => {
          const lines = indices.map((i) => pd.ice.ice_lines[i]);
          const center = transpose<number>(lines).map(
            (points) => mean(points) ?? 0
          );

          const scores = meanAbsolute(lines, center);

          return [pd.x_feature, mean(scores) ?? 0];
        })
      );

      return data.sort((a, b) =>
        ascending(scores[a.x_feature], scores[b.x_feature])
      );
    },
  },
  {
    name: 'highlighted distribution',
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

          const overall = normalize(
            featureInfo[pd.x_feature].distribution.counts
          );
          const highlighted = normalize(highlightedDistribution.counts);

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
    name: 'interaction',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.H, b.H));
    },
  },
  {
    name: 'variance',
    forBrushing: false,
    sort: function (data: OneWayPD[] | TwoWayPD[]): OneWayPD[] | TwoWayPD[] {
      if (data.length === 0 || isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
];
