// dataset
export type Dataset = Record<string, number[]>;

// Features

export type OneHotFeatureInfo = {
  kind: 'categorical';
  subkind: 'one_hot';
  ordered: false;
  values: number[];
  distribution: { bins: number[]; counts: number[] };
  columns_and_values: any;
  value_to_column: any;
  value_map: Record<number, string>;
};

export type NominalFeatureInfo = {
  kind: 'categorical';
  subkind: 'nominal';
  ordered: false;
  values: number[];
  distribution: { bins: number[]; counts: number[] };
  value_map: Record<number, string>;
};

export type OrdinalFeatureInfo = {
  kind: 'categorical';
  subkind: 'ordinal';
  ordered: true;
  values: number[];
  distribution: { bins: number[]; counts: number[] };
  value_map: Record<number, string>;
};

export type ContinuousFeatureInfo = {
  kind: 'quantitative';
  subkind: 'continuous';
  ordered: true;
  values: number[];
  distribution: { bins: number[]; counts: number[] };
};

export type DiscreteFeatureInfo = {
  kind: 'quantitative';
  subkind: 'discrete';
  ordered: true;
  values: number[];
  distribution: { bins: number[]; counts: number[] };
};

export type QuantitativeFeatureInfo =
  | ContinuousFeatureInfo
  | DiscreteFeatureInfo;
export type CategoricalFeatureInfo =
  | OneHotFeatureInfo
  | NominalFeatureInfo
  | OrdinalFeatureInfo;
export type FeatureInfo = QuantitativeFeatureInfo | CategoricalFeatureInfo;

// ICE

export type ICE = {
  ice_min: number;
  ice_max: number;
  centered_ice_min: number;
  centered_ice_max: number;
  mean_min: number;
  mean_max: number;
  centered_mean_min: number;
  centered_mean_max: number;
  p10_min: number;
  p90_max: number;
  // TODO: not needed?
  centered_ice_lines: number[][];
  clusters: {
    id: number;
    centered_ice_lines: number[][];
    p10: number[];
    p25: number[];
    p75: number[];
    p90: number[];
    mean: number[];
    centered_mean: number[];
  }[];
  centered_pdp: number[];
  cluster_distance: number;
  interacting_features: string[];
  cluster_labels: number[];
};

export type ICELevel = 'none' | 'mean' | 'band' | 'line';

// partial dependence

export type OrderedOneWayPD = {
  num_features: 1;
  ordered: true;
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

export type UnorderedOneWayPD = {
  num_features: 1;
  ordered: false;
  id: string;
  x_feature: string;
  x_values: number[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  deviation: number;
  distance_to_cluster_center: number;
  cluster: number;
  ice: ICE;
};

export type OneWayPD = UnorderedOneWayPD | OrderedOneWayPD;

export type TwoWayPD = {
  num_features: 2;
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

export type PDSortingOption = {
  name: string;
  sort: (data: OneWayPD[] | TwoWayPD[]) => OneWayPD[] | TwoWayPD[];
};

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
  categoricalPds: Map<number, UnorderedOneWayPD[]>;
  quantitativePds: Map<number, OrderedOneWayPD[]>;
};

// type predicates

export function isOrderedOneWayPd(data: OneWayPD): data is OrderedOneWayPD {
  return data.ordered === true;
}

export function isUnorderedOneWayPd(data: OneWayPD): data is UnorderedOneWayPD {
  return data.ordered === false;
}

export function isOneWayPdArray(
  data: OneWayPD[] | TwoWayPD[]
): data is OneWayPD[] {
  if (data.length === 0) {
    return true;
  }

  return data[0].num_features === 1;
}

// tabs

export type Mode = 'grid' | 'clusters' | 'individual';
