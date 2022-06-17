export type QuantitativeSinglePDPData = {
  type: 'quantitative-single';
  id: string;
  x_feature: string;
  values: {
    x: number;
    avg_pred: number;
  }[];
};

export type CategoricalSinglePDPData = {
  type: 'categorical-single';
  id: string;
  x_feature: string;
  values: {
    x: string | number;
    avg_pred: number;
  }[];
};

export type SinglePDPData =
  | CategoricalSinglePDPData
  | QuantitativeSinglePDPData;

export type QuantitativeDoublePDPData = {
  type: 'quantitative-double';
  id: string;
  x_feature: string;
  y_feature: string;
  x_axis: number[];
  y_axis: number[];
  values: {
    x: number;
    y: number;
    row: number;
    col: number;
    avg_pred: number;
  }[];
};

export type CategoricalDoublePDPData = {
  type: 'categorical-double';
  id: string;
  x_feature: string;
  y_feature: string;
  x_axis: number[] | string[];
  y_axis: number[] | string[];
  values: {
    x: string | number;
    y: string | number;
    row: number;
    col: number;
    avg_pred: number;
  }[];
};

export type MixedDoublePDPData = {
  type: 'mixed-double';
  id: string;
  x_feature: string;
  y_feature: string;
  x_axis: number[];
  y_axis: number[] | string[];
  values: {
    x: number;
    y: string | number;
    row: number;
    col: number;
    avg_pred: number;
  }[];
};

export type DoublePDPData =
  | QuantitativeDoublePDPData
  | CategoricalDoublePDPData
  | MixedDoublePDPData;

export type PDPData = SinglePDPData | DoublePDPData;
