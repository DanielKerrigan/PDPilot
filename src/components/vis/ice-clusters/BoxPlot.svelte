<script lang="ts">
  import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
  import {
    range,
    rollup,
    bisectRight,
    min,
    max,
    quantileSorted,
    ascending,
  } from 'd3-array';
  import { format } from 'd3-format';
  import { stack, stackOffsetExpand, stackOffsetNone } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { Dataset, FeatureInfo, OneWayPD } from '../../../types';
  import { categoricalColors, defaultFormat } from '../../../vis-utils';
  import YAxis from '../axis/YAxis.svelte';
  import XAxis from '../axis/XAxis.svelte';
  import type { InternMap } from 'd3-array';
  import type { Series } from 'd3-shape';

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

  type CategoricalFeatureData = {
    feature: string;
    kind: 'categorical';
    data: Series<PointData, number>[];
  };

  type QuantitativeFeatureData = {
    feature: string;
    kind: 'quantitative';
    data: {
      cluster: number;
      box: {
        min: number;
        q1: number;
        median: number;
        q3: number;
        max: number;
      };
    }[];
  };

  type FeatureData = CategoricalFeatureData | QuantitativeFeatureData;

  let distributions: FeatureData[] = [];

  $: distributions = features.map((f) => {
    const info = $feature_info[f];

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

      return {
        feature: f,
        kind: 'categorical',
        data: stackGenerator(Array.from(aggregate)),
      };
    } else if (info.kind === 'categorical') {
      const aggregate = rollup(
        filteredI,
        (group) => group.length,
        // first group by value
        (i) => $dataset[f][i],
        // then group by cluster
        (i) => pd.ice.cluster_labels[i]
      );

      return {
        feature: f,
        kind: 'categorical',
        data: stackGenerator(Array.from(aggregate)),
      };
    } else {
      const aggregate = rollup(
        filteredI,
        (group) => {
          const values = group.map((i) => $dataset[f][i]).sort(ascending);
          return {
            min: min(values) ?? 0,
            q1: quantileSorted(values, 0.25) ?? 0,
            median: quantileSorted(values, 0.5) ?? 0,
            q3: quantileSorted(values, 0.75) ?? 0,
            max: max(values) ?? 0,
          };
        },
        // group by cluster
        (i) => pd.ice.cluster_labels[i]
      );
      return {
        feature: f,
        kind: 'quantitative',
        data: Array.from(aggregate, ([cluster, box]) => ({
          cluster,
          box,
        })),
      };
    }
  });

  $: x = Object.fromEntries(
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

  function isCategorical(
    featureData: FeatureData
  ): featureData is CategoricalFeatureData {
    return featureData.kind === 'categorical';
  }

  $: y = scaleLinear()
    .domain([
      0,
      normalize
        ? 1
        : Math.max(
            ...distributions
              .filter(isCategorical)
              .map((d) => d.data)
              .flat(3)
          ),
    ])
    .range([fy.bandwidth() - margin.bottom, margin.top]);

  $: yBox = scaleBand<number>()
    .domain(clusterIds)
    .range([fy.bandwidth() - margin.bottom, margin.top])
    .padding(0.25);

  function getValueMap(feature: FeatureInfo) {
    return 'value_map' in feature ? feature.value_map : {};
  }

  function getWidth(valueOrIndex: number, feature: string): number {
    const scale = x[feature];

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
    const scale = x[feature];

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

  $: console.log(distributions);
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
    {#each distributions as d}
      <g transform="translate(0,{fy(d.feature)})">
        {#if d.kind === 'categorical'}
          <g>
            {#each d.data as series, i}
              <g fill={color(i)}>
                {#each series as point}
                  {#if point[0] !== point[1]}
                    <rect
                      x={getX(point.data[0], d.feature) + 1}
                      width={getWidth(point.data[0], d.feature) - 2}
                      y={y(point[1])}
                      height={y(point[0]) - y(point[1])}
                      on:click={() =>
                        toggleFilter(d.feature, series.key, point.data[0])}
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
        {:else}
          <g>
            {#each d.data as { cluster, box }}
              <g transform="translate(0,{yBox(cluster)})">
                <!-- IQR -->
                <rect
                  x={x[d.feature](box.q1) ?? 0}
                  width={(x[d.feature](box.q3) ?? 0) -
                    (x[d.feature](box.q1) ?? 0)}
                  height={yBox.bandwidth()}
                  fill={color(cluster)}
                />

                <!-- median -->
                <line
                  x1={x[d.feature](box.median) ?? 0}
                  x2={x[d.feature](box.median) ?? 0}
                  stroke-width={2}
                  y1={0}
                  y2={yBox.bandwidth()}
                  stroke={'white'}
                />

                <!-- whiskers -->
                <line
                  x1={x[d.feature](box.min) ?? 0}
                  x2={x[d.feature](box.q1) ?? 0}
                  stroke-width={2}
                  y1={yBox.bandwidth() / 2}
                  y2={yBox.bandwidth() / 2}
                  stroke={color(cluster)}
                />

                <line
                  x1={x[d.feature](box.q3) ?? 0}
                  x2={x[d.feature](box.max) ?? 0}
                  stroke-width={2}
                  y1={yBox.bandwidth() / 2}
                  y2={yBox.bandwidth() / 2}
                  stroke={color(cluster)}
                />
              </g>
            {/each}
          </g>
        {/if}

        <XAxis
          scale={x[d.feature]}
          y={fy.bandwidth() - margin.bottom}
          showBaseline={true}
          baselineColor={'var(--gray-6)'}
          tickColor={'var(--gray-6)'}
          integerOnly={$feature_info[d.feature].subkind === 'discrete'}
          value_map={getValueMap($feature_info[d.feature])}
          label={d.feature}
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
