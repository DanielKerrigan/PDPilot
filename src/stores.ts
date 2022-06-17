import type { Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';

import { writable } from 'svelte/store';
import type { DoublePDPData, SinglePDPData } from './types';

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
export const is_calculating = WidgetWritable<boolean>('is_calculating', false);
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

// Set the model for each store you create.
export function setStoreModels(model: DOMWidgetModel): void {
  features.setModel(model);
  selected_features.setModel(model);
  single_pdps.setModel(model);
  double_pdps.setModel(model);
  is_calculating.setModel(model);
  resolution.setModel(model);
  num_instances_used.setModel(model);
  plot_button_clicked.setModel(model);
  total_num_instances.setModel(model);
}
