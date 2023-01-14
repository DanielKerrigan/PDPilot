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
  import { stack, stackOffsetExpand, stackOffsetNone, area } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { Dataset, FeatureInfo, OneWayPD } from '../../../types';
  import { categoricalColors, defaultFormat } from '../../../vis-utils';
  import YAxis from '../axis/YAxis.svelte';
  import XAxis from '../axis/XAxis.svelte';
  import { select } from 'd3-selection';
  import { brushX as d3brushX } from 'd3-brush';
  import type { InternMap } from 'd3-array';
  import type { Series } from 'd3-shape';
  import type { Selection } from 'd3-selection';
  import type { D3BrushEvent } from 'd3-brush';
  import { kernelDensityEstimation } from 'simple-statistics';

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

  type Filter = {
    feature: string;
    cluster: number;
    valueOrIndex: number;
  };

  let filters: Filter[] = [];
  $: filters = [];

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
        low: number;
        q1: number;
        median: number;
        q3: number;
        high: number;
        densities: {
          y: number;
          density: number;
        }[];
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

          // const scale = x[f];

          // const thresholds = 'bandwidth' in scale ? [] : scale.ticks(50);

          // if (thresholds[0] !== info.values[0]) {
          //   thresholds.unshift(info.values[0]);
          // }

          // if (
          //   thresholds[thresholds.length - 1] !==
          //   info.values[info.values.length - 1]
          // ) {
          //   thresholds.push(info.values[info.values.length - 1]);
          // }

          const kde = kernelDensityEstimation(values);
          const densities = info.values.map((y) => ({ y, density: kde(y) }));

          const q1 = quantileSorted(values, 0.25) ?? 0;
          const q3 = quantileSorted(values, 0.75) ?? 0;
          const iqr = q3 - q1;

          const lowThreshold = q1 - iqr * 1.5;
          const highThreshold = q3 + iqr * 1.5;

          const low =
            min(values, (d) =>
              d >= lowThreshold ? d : Number.POSITIVE_INFINITY
            ) ?? 0;
          const high =
            max(values, (d) =>
              d <= highThreshold ? d : Number.NEGATIVE_INFINITY
            ) ?? 0;

          return {
            low,
            q1,
            median: quantileSorted(values, 0.5) ?? 0,
            q3,
            high,
            densities: densities,
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
    .padding(0.05);

  // $: maxDensity =
  //   max(distributions.filter(isQuantitative), (dist) =>
  //     max(dist.data, (cluster) =>
  //       max(cluster.box.densities, (point) => point.density)
  //     )
  //   ) ?? 0;

  // $: violinHeight = scaleLinear()
  //   .domain([0, maxDensity])
  //   .range([0, yBox.bandwidth() / 2]);

  function getViolinPath(
    feature: string,
    densities: { y: number; density: number }[]
  ) {
    const violinHeight = scaleLinear()
      .domain([0, max(densities, (d) => d.density) ?? 0])
      .range([0, yBox.bandwidth() / 2]);

    const violinArea = area<{ y: number; density: number }>()
      .x((d) => x[feature](d.y) ?? 0)
      .y0((d) => -violinHeight(d.density))
      .y1((d) => violinHeight(d.density));

    return violinArea(densities);
  }

  $: boxWidth = Math.min(5, yBox.bandwidth() / 2);

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

  // interaction

  const brushHeight = 20;
  const selectedRanges = new Map<
    string,
    | { kind: 'quantitative'; left: number; right: number }
    | { kind: 'categorical'; categories: number[] }
  >();

  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    const feature = this.id.split('-', 2)[1];

    if (selection === null) {
      selectedRanges.delete(feature);
    } else {
      const [x1, x2] = selection as [number, number];

      const scale = x[feature];

      if ('bandwidth' in scale) {
        const categories = scale.domain().filter((d) => {
          const minX = scale(d) ?? 0;
          const maxY = minX + scale.bandwidth();
          return x1 <= maxY && x2 >= minX;
        });
        selectedRanges.set(feature, { kind: 'categorical', categories });
      } else {
        const left = scale.invert(x1);
        const right = scale.invert(x2);
        selectedRanges.set(feature, { kind: 'quantitative', left, right });
      }
    }

    filteredI = I.filter((i) =>
      Array.from(selectedRanges).every(([feature, range]) => {
        const info = $feature_info[feature];

        if (range.kind === 'quantitative' && info.kind === 'quantitative') {
          const value = $dataset[feature][i];
          return value >= range.left && value <= range.right;
        } else if (range.kind === 'categorical' && info.subkind === 'one_hot') {
          const cols = info.columns_and_values.map((d) => d[0]);
          const value = cols
            .map((col: string) => $dataset[col][i])
            .findIndex((d: number) => d === 1);
          return range.categories.includes(value);
        } else if (
          range.kind === 'categorical' &&
          info.kind === 'categorical'
        ) {
          const value = $dataset[feature][i];
          return range.categories.includes(value);
        } else {
          return false;
        }
      })
    );
  }

  $: brush = d3brushX<undefined>()
    .extent([
      [margin.left, -brushHeight / 2 + fy.bandwidth() - margin.bottom],
      [width - margin.right, brushHeight / 2 + fy.bandwidth() - margin.bottom],
    ])
    .on('start brush end', brushed);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, SVGElement, undefined>;

  $: if (group) {
    selection = select(group).selectAll('.x-axis');
    selection.call(brush);
  }
</script>

<div>
  <div style:height="{checkBoxHeight}px" class="controls-container">
    <label class="label-and-input">
      <input type="checkbox" bind:checked={normalize} />Normalize
    </label>
  </div>
  <svg {width} height={visHeight}>
    <g bind:this={group}>
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
                <g
                  transform="translate(0,{(yBox(cluster) ?? 0) +
                    yBox.bandwidth() / 2})"
                >
                  <!-- KDE -->
                  <path
                    d={getViolinPath(d.feature, box.densities)}
                    fill={color(cluster)}
                  />

                  <!-- IQR -->
                  <rect
                    x={x[d.feature](box.q1) ?? 0}
                    width={(x[d.feature](box.q3) ?? 0) -
                      (x[d.feature](box.q1) ?? 0)}
                    y={-boxWidth / 2}
                    height={boxWidth}
                    fill="var(--gray-1)"
                  />

                  <!-- median -->
                  <line
                    x1={x[d.feature](box.median) ?? 0}
                    x2={x[d.feature](box.median) ?? 0}
                    stroke-width={2}
                    y1={-boxWidth / 2}
                    y2={boxWidth / 2}
                    stroke={'black'}
                  />

                  <!-- whiskers -->
                  <line
                    x1={x[d.feature](box.low) ?? 0}
                    x2={x[d.feature](box.q1) ?? 0}
                    stroke-width={1}
                    stroke="var(--gray-1)"
                  />

                  <line
                    x1={x[d.feature](box.q3) ?? 0}
                    x2={x[d.feature](box.high) ?? 0}
                    stroke-width={1}
                    stroke="var(--gray-1)"
                  />
                </g>
              {/each}
            </g>
          {/if}

          <g class="x-axis" id="axis-{d.feature}">
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
        </g>
      {/each}
    </g>
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
