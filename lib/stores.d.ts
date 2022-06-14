import type { Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';
import type { DoublePDPData, SinglePDPData } from './types';
interface WidgetWritable<T> extends Writable<T> {
    setModel: (m: DOMWidgetModel) => void;
}
export declare function WidgetWritable<T>(name_: string, value_: T): WidgetWritable<T>;
export declare const features: WidgetWritable<string[]>;
export declare const selected_features: WidgetWritable<string[]>;
export declare const single_pdps: WidgetWritable<SinglePDPData[]>;
export declare const double_pdps: WidgetWritable<DoublePDPData[]>;
export declare const is_calculating: WidgetWritable<boolean>;
export declare const resolution: WidgetWritable<number>;
export declare const num_instances_used: WidgetWritable<number>;
export declare const plot_button_clicked: WidgetWritable<number>;
export declare const total_num_instances: WidgetWritable<number>;
export declare function setStoreModels(model: DOMWidgetModel): void;
export {};
