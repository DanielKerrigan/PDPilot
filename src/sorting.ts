import type {
  ClustersSortingOption,
  SinglePDPData,
  DoublePDPData,
  PDSortingOption,
  OneWayQuantitativeCluster,
} from './types';

import { isOneWayPdArray } from './types';

import { ascending, descending } from 'd3-array';

export {
  singlePDPSortingOptions,
  doublePDPSortingOptions,
  oneWayClustersSortingOptions,
};

const singlePDPSortingOptions: PDSortingOption[] = [
  {
    name: 'complexity',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || !isOneWayPdArray(data)) {
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
      if (data.length === 0 || !isOneWayPdArray(data)) {
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
      if (data.length === 0 || !isOneWayPdArray(data)) {
        return data;
      }

      return data.sort((a, b) => ascending(a.x_feature, b.x_feature));
    },
  },
];

const doublePDPSortingOptions: PDSortingOption[] = [
  {
    name: 'H-statistic',
    sort: function (
      data: SinglePDPData[] | DoublePDPData[]
    ): SinglePDPData[] | DoublePDPData[] {
      if (data.length === 0 || isOneWayPdArray(data)) {
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
      if (data.length === 0 || isOneWayPdArray(data)) {
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
      if (data.length === 0 || isOneWayPdArray(data)) {
        return data;
      }

      data.sort((a, b) => ascending(a.y_feature, b.y_feature));
      return data.sort((a, b) => ascending(a.x_feature, b.x_feature));
    },
  },
];

const oneWayClustersSortingOptions: ClustersSortingOption[] = [
  {
    name: 'distance',
    sort: function (
      data: OneWayQuantitativeCluster[]
    ): OneWayQuantitativeCluster[] {
      if (data.length === 0) {
        return data;
      }

      return data.sort((a, b) => ascending(a.mean_distance, b.mean_distance));
    },
  },
];
