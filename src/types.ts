export type QuantitativeSinglePDPData = {
  num_features: 1;
  kind: 'quantitative';
  id: string;
  x_feature: string;
  x_values: number[];
  mean_predictions: number[];
  min_prediction: number;
  max_prediction: number;
  trend_low_order: number[];
  rmse_low_order: number;
  trend_good_fit: number[];
  nrmse_good_fit: number;
  knots_good_fit: number;
  deviation: number;
};

export type CategoricalSinglePDPData = {
  num_features: 1;
  kind: 'categorical';
  id: string;
  x_feature: string;
  x_values: (number | string)[];
  mean_predictions: number[];
  min_prediction: number;
  max_prediction: number;
  rmse_low_order: number;
  nrmse_good_fit: number;
  knots_good_fit: number;
  deviation: number;
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
  min_prediction: number;
  max_prediction: number;
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
  min_prediction: number;
  max_prediction: number;
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
  min_prediction: number;
  max_prediction: number;
  interactions: number[];
  deviation: number;
  H: number;
};

export type DoublePDPData =
  | QuantitativeDoublePDPData
  | CategoricalDoublePDPData
  | MixedDoublePDPData;

export type SortingOption = {
  name: string;
  sort: (
    data: SinglePDPData[] | DoublePDPData[]
  ) => SinglePDPData[] | DoublePDPData[];
};

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
