import type { SinglePDPData, DoublePDPData, SortingOption } from './types';

import { ascending, descending } from 'd3-array';

export { singlePDPSortingOptions, doublePDPSortingOptions };

function isSingle(
  data: SinglePDPData[] | DoublePDPData[]
): data is SinglePDPData[] {
  if (data.length === 0) {
    return true;
  }

  return data[0].num_features === 1;
}

const singlePDPSortingOptions: SortingOption[] = [
  {
    name: 'complexity',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || !isSingle(data)) {
        return data;
      }

      data.sort((a, b) => descending(a.nrmse_good_fit, b.nrmse_good_fit));
      return data.sort((a, b) =>
        descending(a.knots_good_fit, b.knots_good_fit)
      );
    },
  },
  {
    name: 'variance',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || !isSingle(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
  {
    name: 'alphabetical',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || !isSingle(data)) {
        return data;
      }

      return data.sort((a, b) => ascending(a.x_feature, b.x_feature));
    },
  },
];

const doublePDPSortingOptions: SortingOption[] = [
  {
    name: 'H-statistic',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || isSingle(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.H, b.H));
    },
  },
  {
    name: 'variance',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || isSingle(data)) {
        return data;
      }

      return data.sort((a, b) => descending(a.deviation, b.deviation));
    },
  },
  {
    name: 'alphabetical',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || isSingle(data)) {
        return data;
      }

      data.sort((a, b) => ascending(a.y_feature, b.y_feature));
      return data.sort((a, b) => ascending(a.x_feature, b.x_feature));
    },
  },
];
