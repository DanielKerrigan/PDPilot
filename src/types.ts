// ICE

export type ICE = {
  ice_min: number;
  ice_max: number;
  mean_min: number;
  mean_max: number;
  clusters: {
    id: number;
    ice_lines: number[][];
    mean: number[];
  }[];
  cluster_distance: number;
};

// partial dependence

export type QuantitativeSinglePDPData = {
  num_features: 1;
  kind: 'quantitative';
  id: string;
  x_feature: string;
  x_values: number[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  trend_good_fit: number[];
  nrmse_good_fit: number;
  knots_good_fit: number;
  deviation: number;
  distance_to_cluster_center: number;
  cluster: number;
  ice: ICE;
};

export type CategoricalSinglePDPData = {
  num_features: 1;
  kind: 'categorical';
  id: string;
  x_feature: string;
  x_values: (number | string)[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  nrmse_good_fit: number;
  knots_good_fit: number;
  deviation: number;
  distance_to_cluster_center: number;
  cluster: number;
  ice: ICE;
};

export type SinglePDPData =
  | CategoricalSinglePDPData
  | QuantitativeSinglePDPData;

export type QuantitativeDoublePDPData = {
  num_features: 2;
  kind: 'quantitative';
  id: string;
  x_feature: string;
  x_values: number[];
  x_axis: number[];
  y_feature: string;
  y_values: number[];
  y_axis: number[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  interactions: number[];
  deviation: number;
  H: number;
};

export type CategoricalDoublePDPData = {
  num_features: 2;
  kind: 'categorical';
  id: string;
  x_feature: string;
  x_values: (string | number)[];
  x_axis: (string | number)[];
  y_feature: string;
  y_values: (string | number)[];
  y_axis: (string | number)[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  interactions: number[];
  deviation: number;
  H: number;
};

export type MixedDoublePDPData = {
  num_features: 2;
  kind: 'mixed';
  id: string;
  x_feature: string;
  x_values: number[];
  x_axis: number[];
  y_feature: string;
  y_values: (string | number)[];
  y_axis: (string | number)[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  interactions: number[];
  deviation: number;
  H: number;
};

export type DoublePDPData =
  | QuantitativeDoublePDPData
  | CategoricalDoublePDPData
  | MixedDoublePDPData;

export type PDSortingOption = {
  name: string;
  sort: (
    data: SinglePDPData[] | DoublePDPData[]
  ) => SinglePDPData[] | DoublePDPData[];
};

// marginal distributions

export type QuantitativeMarginalDistribution = {
  kind: 'quantitative';
  bins: number[];
  counts: number[];
};

export type CategoricalMarginalDistribution = {
  kind: 'categorical';
  bins: string[];
  counts: number[];
};

export type MarginalDistribution =
  | QuantitativeMarginalDistribution
  | CategoricalMarginalDistribution;

// clusters

export type OneWayQuantitativeCluster = {
  kind: 'quantitative';
  id: number;
  mean_distance: number;
  features: string[];
};

export type OneWayCategoricalCluster = {
  kind: 'categorical';
  id: number;
  features: string[];
};

export type Clusters = {
  categoricalClusters: OneWayCategoricalCluster[];
  quantitativeClusters: OneWayQuantitativeCluster[];
  categoricalPds: Map<number, CategoricalSinglePDPData[]>;
  quantitativePds: Map<number, QuantitativeSinglePDPData[]>;
};

// type predicates

export function isQuantitativeOneWayPd(
  data: SinglePDPData
): data is QuantitativeSinglePDPData {
  return data.kind === 'quantitative';
}

export function isCategoricalOneWayPd(
  data: SinglePDPData
): data is CategoricalSinglePDPData {
  return data.kind === 'categorical';
}

export function isOneWayPdArray(
  data: SinglePDPData[] | DoublePDPData[]
): data is SinglePDPData[] {
  if (data.length === 0) {
    return true;
  }

  return data[0].num_features === 1;
}

export function isQuantitativeOneWayPdArray(
  data: QuantitativeSinglePDPData[] | CategoricalSinglePDPData[]
): data is QuantitativeSinglePDPData[] {
  if (data.length === 0) {
    return true;
  }

  return data[0].kind === 'quantitative';
}

// tabs

export type Mode = 'grid' | 'clusters' | 'individual';
