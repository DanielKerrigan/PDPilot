import { derived, writable } from 'svelte/store';
import type { Readable, Writable } from 'svelte/store';
import type { DOMWidgetModel } from '@jupyter-widgets/base';

import type {
  Dataset,
  TwoWayPD,
  OneWayPD,
  FeatureInfo,
  Tab,
  Distribution,
} from './types';

import { scaleSequential, scaleDiverging } from 'd3-scale';
import type { ScaleSequential, ScaleDiverging } from 'd3-scale';
import { interpolateYlGnBu, interpolateBrBG } from 'd3-scale-chromatic';
import { getHighlightedBins } from './vis-utils';

/**
 *
 * @param name_ Name of the variable in the model. This is the same as the
 *              name of the corresponding Python variable in widget.py
 * @param value_ Default value
 * @param model backbone model containing state synced between Python and JS
 * @returns Svelte store that is synced with the model.
 */
function createSyncedWidget<T>(
  name_: string,
  value_: T,
  model: DOMWidgetModel
): Writable<T> {
  const name: string = name_;
  const internalWritable: Writable<T> = writable(value_);

  // TODO: type this
  const modelValue = model.get(name);
  if (modelValue !== undefined) {
    internalWritable.set(modelValue);
  }

  // when the model changes, update the store
  model.on('change:' + name, () => internalWritable.set(model.get(name)), null);

  return {
    // when the store changes, update the model
    set: (v: T) => {
      internalWritable.set(v);
      if (model) {
        model.set(name, v);
        model.save_changes();
      }
    },
    subscribe: internalWritable.subscribe,
    update: (func: (v: T) => T) => {
      internalWritable.update((v: T) => {
        const output = func(v);
        if (model) {
          model.set(name, output);
          model.save_changes();
        }
        return output;
      });
    },
  };
}

// Stores that are synced with traitlets

export let feature_names: Writable<string[]>;
export let feature_info: Writable<Record<string, FeatureInfo>>;

export let dataset: Writable<Dataset>;

export let num_instances: Writable<number>;

export let one_way_pds: Writable<OneWayPD[]>;
export let two_way_pds: Writable<TwoWayPD[]>;

export let two_way_pdp_extent: Writable<[number, number]>;
export let two_way_interaction_extent: Writable<[number, number]>;

export let ice_line_extent: Writable<[number, number]>;
export let ice_cluster_center_extent: Writable<[number, number]>;
export let centered_ice_line_extent: Writable<[number, number]>;

export let height: Writable<number>;

export let highlighted_indices: Writable<number[]>;

export let two_way_to_calculate: Writable<string[]>;

// Stores that are not synced with traitlets

export let selectedTab: Writable<Tab>;

export let detailedFeature1: Writable<string>;
export let detailedFeature2: Writable<string>;

// is a brush currently being moved over a plot
export let brushingInProgress: Writable<boolean>;
export let brushedFeature: Writable<string>;

export let globalColorTwoWayPdp: Readable<ScaleSequential<string, string>>;

export let globalColorTwoWayInteraction: Readable<
  ScaleDiverging<string, string>
>;

export let featureToPd: Readable<Map<string, OneWayPD>>;

export let highlightedDistributions: Readable<Map<string, Distribution>>;

/**
 * Note that when the cell containing the widget is re-run, a new model is
 * created. We don't want the former model to hang around. We don't want state
 * to carry over when the widget is re-run. That's why all of the stores are
 * initialized in this function, which is called when the widget's cell is run.
 * @param model backbone model that contains state synced between Python and JS
 */
export function setStores(model: DOMWidgetModel): void {
  // stores synced with Python

  feature_names = createSyncedWidget<string[]>('feature_names', [], model);
  feature_info = createSyncedWidget<Record<string, FeatureInfo>>(
    'feature_info',
    {},
    model
  );

  dataset = createSyncedWidget<Dataset>('dataset', {}, model);

  num_instances = createSyncedWidget<number>('num_instances', 0, model);

  one_way_pds = createSyncedWidget<OneWayPD[]>('one_way_pds', [], model);
  two_way_pds = createSyncedWidget<TwoWayPD[]>('two_way_pds', [], model);

  two_way_pdp_extent = createSyncedWidget<[number, number]>(
    'two_way_pdp_extent',
    [0, 0],
    model
  );
  two_way_interaction_extent = createSyncedWidget<[number, number]>(
    'two_way_interaction_extent',
    [0, 0],
    model
  );

  ice_line_extent = createSyncedWidget<[number, number]>(
    'ice_line_extent',
    [0, 0],
    model
  );
  ice_cluster_center_extent = createSyncedWidget<[number, number]>(
    'ice_cluster_center_extent',
    [0, 0],
    model
  );
  centered_ice_line_extent = createSyncedWidget<[number, number]>(
    'centered_ice_line_extent',
    [0, 0],
    model
  );

  height = createSyncedWidget<number>('height', 600, model);

  highlighted_indices = createSyncedWidget<number[]>(
    'highlighted_indices',
    [],
    model
  );

  two_way_to_calculate = createSyncedWidget<string[]>(
    'two_way_to_calculate',
    [],
    model
  );

  // stores not synced with Python

  selectedTab = writable('one-way-plots');

  const one_ways = model.get('one_way_pds') as OneWayPD[] | undefined;
  const detailedFeature1Default =
    one_ways && one_ways.length > 0 ? one_ways[0].x_feature : '';
  detailedFeature1 = writable(detailedFeature1Default);
  detailedFeature2 = writable('');

  brushingInProgress = writable(false);
  brushedFeature = writable('');

  globalColorTwoWayPdp = derived(two_way_pdp_extent, ($two_way_pdp_extent) =>
    scaleSequential()
      .domain($two_way_pdp_extent)
      .interpolator(interpolateYlGnBu)
      .unknown('black')
  );

  globalColorTwoWayInteraction = derived(
    two_way_interaction_extent,
    ($two_way_interaction_extent) =>
      scaleDiverging<string, string>()
        .domain([
          $two_way_interaction_extent[0],
          0,
          $two_way_interaction_extent[1],
        ])
        .interpolator(interpolateBrBG)
        .unknown('black')
  );

  featureToPd = derived(
    one_way_pds,
    ($one_way_pds) => new Map($one_way_pds.map((d) => [d.x_feature, d]))
  );

  highlightedDistributions = derived(
    [feature_info, dataset, highlighted_indices],
    ([$feature_info, $dataset, $highlighted_indices]) =>
      new Map(
        Object.entries($feature_info).map(([featureName, info]) => {
          const values = $dataset[featureName];
          return [
            featureName,
            getHighlightedBins(info, values, $highlighted_indices),
          ];
        })
      )
  );
}
