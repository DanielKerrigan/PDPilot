// Dataset

export type Dataset = Record<string, number[]>;

// Distribution

export type Distribution = {
  bins: number[];
  counts: number[];
  percents: number[];
};

export type RaincloudData = {
  values: { value: number; label: number }[];
  densities: {
    x: number;
    density: number;
  }[];
  mean: number;
};

// Features

export type OneHotFeatureInfo = {
  kind: 'categorical';
  subkind: 'one_hot';
  ordered: false;
  values: number[];
  distribution: Distribution;
  columns_and_values: [string, string][];
  value_to_column: Record<string, string>;
  value_map: Record<number, string>;
};

export type NominalFeatureInfo = {
  kind: 'categorical';
  subkind: 'nominal';
  ordered: false;
  values: number[];
  distribution: Distribution;
  value_map: Record<number, string>;
};

export type OrdinalFeatureInfo = {
  kind: 'categorical';
  subkind: 'ordinal';
  ordered: true;
  values: number[];
  distribution: Distribution;
  value_map: Record<number, string>;
};

export type ContinuousFeatureInfo = {
  kind: 'quantitative';
  subkind: 'continuous';
  ordered: true;
  values: number[];
  distribution: Distribution;
};

export type DiscreteFeatureInfo = {
  kind: 'quantitative';
  subkind: 'discrete';
  ordered: true;
  values: number[];
  distribution: Distribution;
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

export type Cluster = {
  id: number;
  indices: number[];
  centered_mean: number[];
  distance: number;
};

export type Clustering = {
  clusters: Cluster[];
  cluster_labels: number[];
  cluster_distance: number;
  centered_mean_min: number;
  centered_mean_max: number;
  interacting_features: string[];
};

export type ICE = {
  ice_min: number;
  ice_max: number;
  centered_ice_min: number;
  centered_ice_max: number;
  clusterings: Record<string, Clustering>;
  adjusted_clusterings: Record<string, Clustering>;
  centered_pdp: number[];
  num_clusters: number;
};

export type ICELevel =
  | 'lines'
  | 'centered-lines'
  | 'cluster-centers'
  | 'cluster-lines';

export type ClusterUpdate =
  | {
      feature: string;
      prev_num_clusters: number;
      source_cluster_id: number;
      dest_cluster_id: number;
      indices: number[];
    }
  | Record<string, never>;

// Partial dependence

export type Shape = 'increasing' | 'decreasing' | 'mixed';

export type OrderedOneWayPD = {
  num_features: 1;
  ordered: true;
  id: string;
  x_feature: string;
  x_values: number[];
  mean_predictions: number[];
  pdp_min: number;
  pdp_max: number;
  deviation: number;
  ice: ICE;
  shape: Shape;
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
  interaction_min: number;
  interaction_max: number;
  deviation: number;
  H: number;
};

export type PDSortingOption = {
  name: string;
  forBrushing: boolean;
  sort: (
    data: OneWayPD[] | TwoWayPD[],
    extra?: {
      highlightedIndices?: number[];
      highlightedDistributions?: Map<string, Distribution>;
      featureInfo?: Record<string, FeatureInfo>;
      featureToIceLines?: Record<string, number[][]>;
    }
  ) => OneWayPD[] | TwoWayPD[];
};

// Type predicates

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

// Tabs

export type Tab = 'one-way-plots' | 'two-way-plots' | 'detailed-plot';

// Filtering

export type ShapeSelections = {
  ordered: {
    checked: boolean;
    shapes: Shape[];
  };
  nominal: {
    checked: boolean;
  };
};

// Detailed Plots

export type OneWayDetailedContextKind =
  | 'none'
  | 'cluster-descriptions'
  | 'scatterplot';
