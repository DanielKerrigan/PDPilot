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
  ICELevel,
  OneWayDetailedContextKind,
  ClusterUpdate,
} from './types';

import { scaleSequential, scaleDiverging } from 'd3-scale';
import type { ScaleSequential, ScaleDiverging } from 'd3-scale';
import { interpolateYlGnBu, interpolateBrBG } from 'd3-scale-chromatic';
import { getHighlightedBins, getNiceDomain } from './vis-utils';

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

// ==== Stores that are synced with traitlets ====

export let feature_names: Writable<string[]>;
export let feature_info: Writable<Record<string, FeatureInfo>>;

export let dataset: Writable<Dataset>;

export let labels: Writable<number[]>;

export let num_instances: Writable<number>;

export let one_way_pds: Writable<OneWayPD[]>;
export let feature_to_ice_lines: Writable<Record<string, number[][]>>;
export let two_way_pds: Writable<TwoWayPD[]>;

export let two_way_pdp_extent: Writable<[number, number]>;
export let two_way_interaction_extent: Writable<[number, number]>;

export let one_way_pdp_extent: Writable<[number, number]>;
export let ice_line_extent: Writable<[number, number]>;
export let ice_cluster_center_extent: Writable<[number, number]>;
export let centered_ice_line_extent: Writable<[number, number]>;

export let height: Writable<number>;

export let highlighted_indices: Writable<number[]>;

export let two_way_to_calculate: Writable<string[]>;

export let cluster_update: Writable<ClusterUpdate>;

// ==== Stores that are not synced with traitlets ====

export let selectedTab: Writable<Tab>;

export let featureToPd: Readable<Map<string, OneWayPD>>;

export let isClassification: Readable<boolean>;
export let labelExtent: Readable<[number, number]>;

// detailed plot

export let detailedFeature1: Writable<string>;
export let detailedFeature2: Writable<string>;

export let detailedICELevel: Writable<ICELevel>;
export let detailedContextKind: Writable<OneWayDetailedContextKind>;
export let detailedScaleLocally: Writable<boolean>;

// quasi-random data

export let quasiRandomPoints: Readable<{ x: number; y: number }[]>;

// brushing

// is a brush currently being moved over a plot
export let brushingInProgress: Writable<boolean>;
export let brushedFeature: Writable<string>;

export let highlightedIndicesSet: Readable<Set<number>>;
export let highlightedDistributions: Readable<Map<string, Distribution>>;

// color

export let globalColorTwoWayPdp: Readable<ScaleSequential<string, string>>;

export let globalColorTwoWayInteraction: Readable<
  ScaleDiverging<string, string>
>;

/**
 * Note that when the cell containing the widget is re-run, a new model is
 * created. We don't want the former model to hang around. We don't want state
 * to carry over when the widget is re-run. That's why all of the stores are
 * initialized in this function, which is called when the widget's cell is run.
 * @param model backbone model that contains state synced between Python and JS
 */
export function setStores(model: DOMWidgetModel): void {
  // ==== stores synced with Python ====

  feature_names = createSyncedWidget<string[]>('feature_names', [], model);
  feature_info = createSyncedWidget<Record<string, FeatureInfo>>(
    'feature_info',
    {},
    model
  );

  dataset = createSyncedWidget<Dataset>('dataset', {}, model);

  labels = createSyncedWidget<number[]>('labels', [], model);

  num_instances = createSyncedWidget<number>('num_instances', 0, model);

  one_way_pds = createSyncedWidget<OneWayPD[]>('one_way_pds', [], model);
  feature_to_ice_lines = createSyncedWidget<Record<string, number[][]>>(
    'feature_to_ice_lines',
    {},
    model
  );
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

  one_way_pdp_extent = createSyncedWidget<[number, number]>(
    'one_way_pdp_extent',
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

  cluster_update = createSyncedWidget<ClusterUpdate>(
    'cluster_update',
    {},
    model
  );

  // ==== stores not synced with Python ====

  selectedTab = writable('one-way-plots');

  featureToPd = derived(one_way_pds, ($one_way_pds) => {
    return new Map($one_way_pds.map((d) => [d.x_feature, d]));
  });

  isClassification = derived(labels, ($labels) => new Set($labels).size === 2);

  labelExtent = derived(
    [labels, isClassification],
    ([$labels, $isClassification]) => {
      const minLabel = Math.min(...$labels);
      const maxLabel = Math.max(...$labels);
      const extent = [minLabel, maxLabel] as [number, number];
      return $isClassification ? extent : getNiceDomain(extent);
    }
  );

  // detailed plot

  const one_ways = model.get('one_way_pds') as OneWayPD[] | undefined;
  const detailedFeature1Default =
    one_ways && one_ways.length > 0 ? one_ways[0].x_feature : '';
  detailedFeature1 = writable(detailedFeature1Default);
  detailedFeature2 = writable('');

  detailedICELevel = writable('lines');
  detailedScaleLocally = writable(false);
  detailedContextKind = writable('scatterplot');

  // quasi-random coordinates

  quasiRandomPoints = derived(num_instances, ($num_instances) => {
    const g = 1.324717957244746;
    const a1 = 1.0 / g;
    const a2 = 1.0 / (g * g);
    return Array.from({ length: $num_instances }, (_, i) => ({
      x: (0.5 + a1 * i) % 1,
      y: (0.5 + a2 * i) % 1,
    }));
  });

  // brushing

  brushingInProgress = writable(false);
  brushedFeature = writable('');

  highlightedIndicesSet = derived(
    highlighted_indices,
    ($highlighted_indices) => new Set($highlighted_indices)
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

  // color

  globalColorTwoWayPdp = derived(two_way_pdp_extent, ($two_way_pdp_extent) => {
    return scaleSequential()
      .domain(getNiceDomain($two_way_pdp_extent))
      .interpolator(interpolateYlGnBu)
      .unknown('black');
  });

  globalColorTwoWayInteraction = derived(
    two_way_interaction_extent,
    ($two_way_interaction_extent) => {
      const niceValue = getNiceDomain([0, $two_way_interaction_extent[1]])[1];
      return scaleDiverging<string, string>()
        .domain([-niceValue, 0, niceValue])
        .interpolator(interpolateBrBG)
        .unknown('black');
    }
  );
}
