import { derived, writable } from 'svelte/store';
import type { Readable, Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';

import type {
  UnorderedOneWayPD,
  Dataset,
  TwoWayPD,
  Mode,
  OneWayCategoricalCluster,
  OneWayQuantitativeCluster,
  OrderedOneWayPD,
  OneWayPD,
  FeatureInfo,
} from './types';

import { isUnorderedOneWayPd, isOrderedOneWayPd } from './types';

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
export const feature_names = WidgetWritable<string[]>('feature_names', []);
export const feature_info = WidgetWritable<Record<string, FeatureInfo>>(
  'feature_info',
  {}
);

export const dataset = WidgetWritable<Dataset>('dataset', {});

export const num_instances = WidgetWritable<number>('num_instances', 0);

export const one_way_pds = WidgetWritable<OneWayPD[]>('one_way_pds', []);
export const two_way_pds = WidgetWritable<TwoWayPD[]>('two_way_pds', []);

export const pdp_extent = WidgetWritable<[number, number]>(
  'pdp_extent',
  [0, 0]
);
export const ice_mean_extent = WidgetWritable<[number, number]>(
  'ice_mean_extent',
  [0, 0]
);
export const ice_band_extent = WidgetWritable<[number, number]>(
  'ice_band_extent',
  [0, 0]
);
export const ice_line_extent = WidgetWritable<[number, number]>(
  'ice_line_extent',
  [0, 0]
);

export const one_way_quantitative_clusters = WidgetWritable<
  OneWayQuantitativeCluster[]
>('one_way_quantitative_clusters', []);
export const one_way_categorical_clusters = WidgetWritable<
  OneWayCategoricalCluster[]
>('one_way_categorical_clusters', []);

export const height = WidgetWritable<number>('height', 600);

// Set the model for each store you create.
export function setStoreModels(model: DOMWidgetModel): void {
  feature_names.setModel(model);
  feature_info.setModel(model);

  dataset.setModel(model);

  num_instances.setModel(model);

  one_way_pds.setModel(model);
  two_way_pds.setModel(model);

  pdp_extent.setModel(model);
  ice_mean_extent.setModel(model);
  ice_band_extent.setModel(model);
  ice_line_extent.setModel(model);

  one_way_quantitative_clusters.setModel(model);
  one_way_categorical_clusters.setModel(model);

  height.setModel(model);
}

// Stores that are not synced with the backend

export const mode: Writable<Mode> = writable('grid');

// Derived stores

// Nice scales extents

export const nice_pdp_extent: Readable<[number, number]> = derived(
  pdp_extent,
  ($pdp_extent) =>
    scaleLinear().domain($pdp_extent).nice().domain() as [number, number]
);

export const nice_ice_mean_extent: Readable<[number, number]> = derived(
  ice_mean_extent,
  ($ice_mean_extent) =>
    scaleLinear().domain($ice_mean_extent).nice().domain() as [number, number]
);

export const nice_ice_band_extent: Readable<[number, number]> = derived(
  ice_band_extent,
  ($ice_band_extent) =>
    scaleLinear().domain($ice_band_extent).nice().domain() as [number, number]
);

export const nice_ice_line_extent: Readable<[number, number]> = derived(
  ice_line_extent,
  ($ice_line_extent) =>
    scaleLinear().domain($ice_line_extent).nice().domain() as [number, number]
);

export const globalColorPdpExtent: Readable<
  d3.ScaleSequential<string, string>
> = derived(nice_pdp_extent, ($nice_pdp_extent) =>
  scaleSequential()
    .domain($nice_pdp_extent)
    .interpolator(interpolateYlGnBu)
    .unknown('black')
);

// Maps of clutered PDs

export const clusteredQuantitativeOneWayPds: Readable<
  Map<number, OrderedOneWayPD[]>
> = derived(one_way_pds, ($single_pdps) => {
  const quantPds = $single_pdps
    .filter(isOrderedOneWayPd)
    .sort((a, b) =>
      ascending(a.distance_to_cluster_center, b.distance_to_cluster_center)
    );
  return group(quantPds, (d) => d.cluster);
});

export const clusteredCategoricalOneWayPds: Readable<
  Map<number, UnorderedOneWayPD[]>
> = derived(one_way_pds, ($single_pdps) => {
  const catPds = $single_pdps
    .filter(isUnorderedOneWayPd)
    .sort((a, b) =>
      ascending(a.distance_to_cluster_center, b.distance_to_cluster_center)
    );
  return group(catPds, (d) => d.cluster);
});
