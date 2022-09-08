import { derived, writable } from 'svelte/store';
import type { Readable, Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';

import type {
  CategoricalSinglePDPData,
  DoublePDPData,
  MarginalDistribution,
  Mode,
  OneWayCategoricalCluster,
  OneWayQuantitativeCluster,
  QuantitativeSinglePDPData,
  SinglePDPData,
} from './types';

import { isCategoricalOneWayPd, isQuantitativeOneWayPd } from './types';

import { scaleLinear, scaleSequential } from 'd3-scale';
import { interpolateYlGnBu } from 'd3-scale-chromatic';
import { group, ascending } from 'd3-array';

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

export const marginal_distributions = WidgetWritable<
  Record<string, MarginalDistribution>
>('marginal_distributions', {});

export const one_way_quantitative_clusters = WidgetWritable<
  OneWayQuantitativeCluster[]
>('one_way_quantitative_clusters', []);

export const one_way_categorical_clusters = WidgetWritable<
  OneWayCategoricalCluster[]
>('one_way_categorical_clusters', []);

export const height = WidgetWritable<number>('height', 600);

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
  marginal_distributions.setModel(model);
  one_way_quantitative_clusters.setModel(model);
  one_way_categorical_clusters.setModel(model);
  height.setModel(model);
}

// Stores that are not synced with the backend

export const mode: Writable<Mode> = writable('grid');

// Derived stores

export const nice_prediction_extent: Readable<[number, number]> = derived(
  prediction_extent,
  ($prediction_extent) =>
    scaleLinear().domain($prediction_extent).nice().domain() as [number, number]
);

export const globalColor: Readable<d3.ScaleSequential<string, string>> =
  derived(nice_prediction_extent, ($nice_prediction_extent) =>
    scaleSequential()
      .domain($nice_prediction_extent)
      .interpolator(interpolateYlGnBu)
      .unknown('black')
  );

export const clusteredQuantitativeOneWayPds: Readable<
  Map<number, QuantitativeSinglePDPData[]>
> = derived(single_pdps, ($single_pdps) => {
  const quantPds = $single_pdps
    .filter(isQuantitativeOneWayPd)
    .sort((a, b) =>
      ascending(a.distance_to_cluster_center, b.distance_to_cluster_center)
    );
  return group(quantPds, (d) => d.cluster);
});

export const clusteredCategoricalOneWayPds: Readable<
  Map<number, CategoricalSinglePDPData[]>
> = derived(single_pdps, ($single_pdps) => {
  const catPds = $single_pdps
    .filter(isCategoricalOneWayPd)
    .sort((a, b) =>
      ascending(a.distance_to_cluster_center, b.distance_to_cluster_center)
    );
  return group(catPds, (d) => d.cluster);
});
