import { derived, writable } from 'svelte/store';
import type { Readable, Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';

import type {
  DoublePDPData,
  MarginalDistribution,
  SinglePDPData,
} from './types';
import { scaleLinear } from 'd3-scale';

interface WidgetWritable<T> extends Writable<T> {
  setModel: (m: DOMWidgetModel) => void;
}

export function WidgetWritable<T>(name_: string, value_: T): WidgetWritable<T> {
  const name: string = name_;
  const internalWritable: Writable<any> = writable(value_);
  let model: DOMWidgetModel;

  return {
    set: (v: any) => {
      internalWritable.set(v);
      if (model) {
        model.set(name, v);
        model.save_changes();
      }
    },
    subscribe: internalWritable.subscribe,
    update: (func: any) => {
      internalWritable.update((v: any) => {
        const output = func(v);
        if (model) {
          model.set(name, output);
          model.save_changes();
        }
        return output;
      });
    },
    setModel: (m: DOMWidgetModel) => {
      model = m;
      const modelValue = model.get(name);
      if (modelValue) {
        internalWritable.set(modelValue);
      }
      model.on(
        'change:' + name,
        () => internalWritable.set(model.get(name)),
        null
      );
    },
  };
}

// Declare stores with their associated Traitlets here.

export const features = WidgetWritable<string[]>('features', []);
export const selected_features = WidgetWritable<string[]>(
  'selected_features',
  []
);
export const single_pdps = WidgetWritable<SinglePDPData[]>('single_pdps', []);
export const double_pdps = WidgetWritable<DoublePDPData[]>('double_pdps', []);
export const resolution = WidgetWritable<number>('resolution', 20);
export const num_instances_used = WidgetWritable<number>(
  'num_instances_used',
  100
);
export const plot_button_clicked = WidgetWritable<number>(
  'plot_button_clicked',
  0
);
export const total_num_instances = WidgetWritable<number>(
  'total_num_instances',
  0
);

export const prediction_extent = WidgetWritable<[number, number]>(
  'prediction_extent',
  [0, 0]
);

export const include_single_pdps = WidgetWritable<boolean>(
  'include_single_pdps',
  true
);
export const include_double_pdps = WidgetWritable<boolean>(
  'include_double_pdps',
  true
);

export const is_calculating_single_pdps = WidgetWritable<boolean>(
  'is_calculating_single_pdps',
  false
);
export const is_calculating_double_pdps = WidgetWritable<boolean>(
  'is_calculating_double_pdps',
  false
);

export const marginal_distributions = WidgetWritable<
  Record<string, MarginalDistribution>
>('marginal_distributions', {});

// Set the model for each store you create.
export function setStoreModels(model: DOMWidgetModel): void {
  features.setModel(model);
  selected_features.setModel(model);
  single_pdps.setModel(model);
  double_pdps.setModel(model);
  resolution.setModel(model);
  num_instances_used.setModel(model);
  plot_button_clicked.setModel(model);
  total_num_instances.setModel(model);
  prediction_extent.setModel(model);
  include_single_pdps.setModel(model);
  include_double_pdps.setModel(model);
  is_calculating_single_pdps.setModel(model);
  is_calculating_double_pdps.setModel(model);
  marginal_distributions.setModel(model);
}

// Derived stores

export const nice_prediction_extent: Readable<[number, number]> = derived(
  prediction_extent,
  ($prediction_extent) =>
    scaleLinear().domain($prediction_extent).nice().domain() as [number, number]
);

export const filteredOneWayPds = derived(
  [single_pdps, selected_features],
  ([$single_pdps, $selected_features]) =>
    $single_pdps.filter((p) => $selected_features.includes(p.x_feature))
);

export const filteredTwoWayPds = derived(
  [double_pdps, selected_features],
  ([$double_pdps, $selected_features]) =>
    $double_pdps.filter(
      (p) =>
        $selected_features.includes(p.x_feature) &&
        $selected_features.includes(p.y_feature)
    )
);
