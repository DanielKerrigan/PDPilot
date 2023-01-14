<script lang="ts">
  import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
  import { range, rollup, bisectRight } from 'd3-array';
  import { format } from 'd3-format';
  import { stack, stackOffsetExpand, stackOffsetNone } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { Dataset, FeatureInfo, OneWayPD } from '../../../types';
  import { categoricalColors, defaultFormat } from '../../../vis-utils';
  import YAxis from '../axis/YAxis.svelte';
  import XAxis from '../axis/XAxis.svelte';
  import type { InternMap } from 'd3-array';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let features: string[];

  const margin = {
    top: 10,
    right: 5,
    bottom: 40,
    left: 50,
  };

  const checkBoxHeight = 20;
  let normalize = false;

  $: visHeight = height - checkBoxHeight;

  $: clusterIds = range(pd.ice.clusters.length);

  $: color = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: fy = scaleBand<string>().domain(features).range([0, visHeight]);

  $: I = range($num_instances);

  type ClusterToCount = InternMap<number, number>;
  type PointData = [number, ClusterToCount];

  $: stackGenerator = stack<PointData, number>()
    .keys(clusterIds)
    .value((d, key) => d[1].get(key) ?? 0)
    .offset(normalize ? stackOffsetExpand : stackOffsetNone);

  type Filter = {
    feature: string;
    cluster: number;
    valueOrIndex: number;
  };

  let filters: Filter[] = [];

  $: filters = [];

  function toggleFilter(
    feature: string,
    cluster: number,
    valueOrIndex: number
  ) {
    const filteredFilters = filters.filter((d) => d.feature !== feature);

    if (filteredFilters.length !== filters.length) {
      filters = filteredFilters;
    } else {
      filters = [...filters, { feature, cluster, valueOrIndex }];
    }
  }

  function clearFilters() {
    filters = [];
  }

  function filterIndices(
    I: number[],
    filters: Filter[],
    dataset: Dataset,
    feature_info: Record<string, FeatureInfo>
  ): number[] {
    if (filters.length === 0) {
      return I;
    }

    return I.filter((i) => {
      for (let { feature, cluster, valueOrIndex } of filters) {
        if (pd.ice.cluster_labels[i] !== cluster) {
          return false;
        }

        const info = feature_info[feature];
        const bins = info.distribution.bins;

        if (info.subkind === 'one_hot') {
          const cols = info.columns_and_values.map((d) => d[0]);
          const value = cols
            .map((col: string) => dataset[col][i])
            .findIndex((d: number) => d === 1);

          if (value !== valueOrIndex) {
            return false;
          }
        } else if (info.kind === 'categorical') {
          if (dataset[feature][i] !== valueOrIndex) {
            return false;
          }
        } else {
          const bin =
            bisectRight(bins, dataset[feature][i], 0, bins.length - 1) - 1;

          if (bin !== valueOrIndex) {
            return false;
          }
        }
      }

      return true;
    });
  }

  $: filteredI = filterIndices(I, filters, $dataset, $feature_info);

  $: data = features.map((f) => {
    const info = $feature_info[f];
    const bins = info.distribution.bins;

    if (info.subkind === 'one_hot') {
      const cols = info.columns_and_values.map((d) => d[0]);
      const vals = I.map((i) =>
        cols
          .map((col: string) => $dataset[col][i])
          .findIndex((d: number) => d === 1)
      );

      const aggregate = rollup(
        filteredI,
        (group) => group.length,
        // first group by value
        (i) => vals[i],
        // then group by cluster
        (i) => pd.ice.cluster_labels[i]
      );

      return stackGenerator(Array.from(aggregate));
    } else if (info.kind === 'categorical') {
      const aggregate = rollup(
        filteredI,
        (group) => group.length,
        // first group by value
        (i) => $dataset[f][i],
        // then group by cluster
        (i) => pd.ice.cluster_labels[i]
      );

      return stackGenerator(Array.from(aggregate));
    } else {
      const aggregate = rollup(
        filteredI,
        (group) => group.length,
        /*
        bins is from np.histogram. From the docs:

        All but the last (righthand-most) bin is half-open.
        In other words, if bins is:

        [1, 2, 3, 4]

        then the first bin is [1, 2) (including 1, but excluding 2)
        and the second [2, 3). The last bin, however, is [3, 4],
        which includes 4.

        -------

        Determine the leftmost index of the bin for a given data point.
        bisectRight returns the index of where the given value should
        be inserted in the array to maintain sorted order. If the value
        is already in the array, then the index after is returned.
        */
        (i) => bisectRight(bins, $dataset[f][i], 0, bins.length - 1) - 1,
        // then group by cluster
        (i) => pd.ice.cluster_labels[i]
      );

      return stackGenerator(Array.from(aggregate));
    }
  });

  $: x = new Map(
    features.map((f) => {
      const info = $feature_info[f];

      const scale =
        info.kind === 'quantitative'
          ? scaleLinear()
              .domain([info.values[0], info.values[info.values.length - 1]])
              .range([margin.left, width - margin.right])
          : scaleBand<number>()
              .domain(info.values)
              .range([margin.left, width - margin.right]);

      return [f, scale];
    })
  );

  $: y = scaleLinear()
    .domain([0, normalize ? 1 : Math.max(...data.flat(3))])
    .range([fy.bandwidth() - margin.bottom, margin.top]);

  function getValueMap(feature: FeatureInfo) {
    return 'value_map' in feature ? feature.value_map : {};
  }

  function getWidth(valueOrIndex: number, feature: string): number {
    const scale = x.get(feature);

    if (!scale) {
      return 0;
    }

    if ('bandwidth' in scale) {
      return scale.bandwidth();
    } else {
      const info = $feature_info[feature];
      return (
        scale(info.distribution.bins[valueOrIndex + 1]) -
        scale(info.distribution.bins[valueOrIndex])
      );
    }
  }

  function getX(valueOrIndex: number, feature: string): number {
    const scale = x.get(feature);

    if (!scale) {
      return 0;
    }

    if ('bandwidth' in scale) {
      return scale(valueOrIndex) ?? 0;
    } else {
      const info = $feature_info[feature];
      return scale(info.distribution.bins[valueOrIndex]);
    }
  }
</script>

<div>
  <div style:height="{checkBoxHeight}px" class="controls-container">
    <label class="label-and-input">
      <input type="checkbox" bind:checked={normalize} />Normalize
    </label>
    <button
      class="small"
      on:click={clearFilters}
      disabled={filters.length === 0}>Clear Filters</button
    >
  </div>
  <svg {width} height={visHeight}>
    {#each features as feature, featureIdx}
      <g transform="translate(0,{fy(feature)})">
        <g>
          {#each data[featureIdx] as series, i}
            <g fill={color(i)}>
              {#each series as point}
                {#if point[0] !== point[1]}
                  <rect
                    x={getX(point.data[0], feature) + 1}
                    width={getWidth(point.data[0], feature) - 2}
                    y={y(point[1])}
                    height={y(point[0]) - y(point[1])}
                    on:click={() =>
                      toggleFilter(feature, series.key, point.data[0])}
                  />
                {/if}
              {/each}
            </g>
          {/each}
        </g>

        <YAxis
          scale={y}
          x={margin.left}
          label={normalize ? 'percent' : 'count'}
          format={normalize ? format('~%') : defaultFormat}
        />

        <XAxis
          scale={x.get(feature) ?? scaleLinear()}
          y={fy.bandwidth() - margin.bottom}
          showBaseline={true}
          baselineColor={'var(--gray-6)'}
          tickColor={'var(--gray-6)'}
          integerOnly={$feature_info[feature].subkind === 'discrete'}
          value_map={getValueMap($feature_info[feature])}
          label={feature}
        />
      </g>
    {/each}
  </svg>
</div>

<style>
  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .controls-container {
    display: flex;
    align-items: center;
    gap: 1em;
  }
</style>
