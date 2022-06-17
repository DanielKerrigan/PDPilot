export declare type QuantitativeSinglePDPData = {
    type: 'quantitative-single';
    id: string;
    x_feature: string;
    values: {
        x: number;
        avg_pred: number;
    }[];
};
export declare type CategoricalSinglePDPData = {
    type: 'categorical-single';
    id: string;
    x_feature: string;
    values: {
        x: string | number;
        avg_pred: number;
    }[];
};
export declare type SinglePDPData = CategoricalSinglePDPData | QuantitativeSinglePDPData;
export declare type QuantitativeDoublePDPData = {
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
export declare type CategoricalDoublePDPData = {
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
export declare type MixedDoublePDPData = {
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
export declare type DoublePDPData = QuantitativeDoublePDPData | CategoricalDoublePDPData | MixedDoublePDPData;
export declare type PDPData = SinglePDPData | DoublePDPData;
