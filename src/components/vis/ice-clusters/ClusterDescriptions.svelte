<script lang="ts">
  import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
  import type { ScaleBand, ScaleLinear } from 'd3-scale';
  import {
    range,
    rollup,
    min,
    max,
    quantileSorted,
    ascending,
    ticks,
  } from 'd3-array';
  import { format } from 'd3-format';
  import {
    stack,
    stackOffsetExpand,
    stackOffsetNone,
    stackOrderReverse,
    area,
  } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { FeatureInfo, OneWayPD } from '../../../types';
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
  import { createEventDispatcher, onMount, tick } from 'svelte';

  export let pd: OneWayPD;
  export let features: string[];

  const margin = {
    top: 10,
    right: 5,
    bottom: 40,
    left: 50,
  };

  let div: HTMLDivElement;
  // we don't pass width and height to this component, primarily so that
  // we can take into account the width of the scroll bar on windows.
  let visWidth = 0;
  let visViewHeight = 0;

  onMount(() => {
    // Adapted from https://blog.sethcorker.com/question/how-do-you-use-the-resize-observer-api-in-svelte/
    // and https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver
    const resizeObserver = new ResizeObserver(
      (entries: ResizeObserverEntry[]) => {
        if (entries.length !== 1) {
          return;
        }

        const entry: ResizeObserverEntry = entries[0];

        if (entry.contentBoxSize) {
          const contentBoxSize = Array.isArray(entry.contentBoxSize)
            ? entry.contentBoxSize[0]
            : entry.contentBoxSize;

          visWidth = contentBoxSize.inlineSize;
          visViewHeight = contentBoxSize.blockSize;
        } else {
          visWidth = entry.contentRect.width;
          visViewHeight = entry.contentRect.height;
        }
      }
    );

    resizeObserver.observe(div);

    return () => resizeObserver.unobserve(div);
  });

  let normalize = false;

  // size of the box plot inside of the violin
  const boxWidth = 5;

  $: visTotalHeight = Math.max(
    visViewHeight,
    features.length *
      (pd.ice.num_clusters * boxWidth * 4 + margin.top + margin.bottom)
  );

  $: cluster_labels = pd.ice.clusters[pd.ice.num_clusters].cluster_labels;

  $: clusterIds = range(pd.ice.num_clusters);

  $: categoricalFeatures = features.filter(
    (f) => $feature_info[f].kind === 'categorical'
  );

  $: color = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  // y-scale for faceting by feature
  $: fy = scaleBand<string>().domain(features).range([0, visTotalHeight]);

  $: I = range($num_instances);
  $: filteredI = range($num_instances);

  // map from cluster ID to number of instances
  type ClusterToCount = InternMap<number, number>;
  // the first number represents the categorical feature value (as a number)
  type PointData = [number, ClusterToCount];

  $: stackGenerator = stack<PointData, number>()
    // "A series (layer) is generated for each key."
    .keys(clusterIds)
    .value((d, key) => d[1].get(key) ?? 0)
    .offset(normalize ? stackOffsetExpand : stackOffsetNone)
    .order(stackOrderReverse);

  // map from the name of a feature to its x scale
  $: x = Object.fromEntries(
    features.map((f) => {
      const info = $feature_info[f];

      const scale =
        info.kind === 'quantitative'
          ? scaleLinear()
              .domain([info.values[0], info.values[info.values.length - 1]])
              .range([margin.left, visWidth - margin.right])
          : scaleBand<number>()
              .domain(info.values)
              .range([margin.left, visWidth - margin.right]);

      return [f, scale];
    })
  );

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
        // box plot data
        low: number;
        q1: number;
        median: number;
        q3: number;
        high: number;
        // violin data
        densities: {
          x: number;
          density: number;
        }[];
      };
    }[];
  };

  type FeatureData = CategoricalFeatureData | QuantitativeFeatureData;

  let distributions: FeatureData[] = [];

  $: distributions = features.map((f) => {
    const info = $feature_info[f];

    if (info.kind === 'categorical') {
      // map from value to cluster to count
      const aggregate = rollup(
        filteredI,
        (group) => group.length,
        // first group by value
        (i) => $dataset[f][i],
        // then group by cluster
        (i) => cluster_labels[i]
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

          let densities: { x: number; density: number }[] = [];

          // computing the KDE requires at least two data points
          if (values.length > 1) {
            const kde = kernelDensityEstimation(values);
            const kdeThresholds = ticks(
              values[0],
              values[values.length - 1],
              20
            );
            // include the min and max values in calculating the densities
            if (kdeThresholds[0] !== values[0]) {
              kdeThresholds.unshift(values[0]);
            }
            if (
              kdeThresholds[kdeThresholds.length - 1] !==
              values[values.length - 1]
            ) {
              kdeThresholds.push(values[values.length - 1]);
            }

            densities = kdeThresholds.map((x) => ({ x, density: kde(x) }));
          }

          const median = quantileSorted(values, 0.5) ?? 0;
          const q1 = quantileSorted(values, 0.25) ?? 0;
          const q3 = quantileSorted(values, 0.75) ?? 0;
          const iqr = q3 - q1;

          const lowThreshold = q1 - iqr * 1.5;
          const highThreshold = q3 + iqr * 1.5;

          // get the smallest value greater than the low threshold
          const low =
            min(values, (d) =>
              d >= lowThreshold ? d : Number.POSITIVE_INFINITY
            ) ?? 0;
          // get the largest value less than the high threshold
          const high =
            max(values, (d) =>
              d <= highThreshold ? d : Number.NEGATIVE_INFINITY
            ) ?? 0;

          return {
            low,
            q1,
            median,
            q3,
            high,
            densities,
          };
        },
        // group by cluster
        (i) => cluster_labels[i]
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

  $: maxCategoryCount = Math.max(
    ...distributions
      .filter(isCategorical)
      .map((d) => d.data)
      .flat(3)
  );

  // y-scale for the bar charts
  $: yBar = scaleLinear()
    .domain([0, normalize ? 1 : maxCategoryCount])
    .range([fy.bandwidth() - margin.bottom, margin.top]);

  // y-scale for faceting the violin plots by cluster
  $: yBox = scaleBand<number>()
    .domain(clusterIds)
    .range([margin.top, fy.bandwidth() - margin.bottom])
    .paddingInner(0.1)
    .paddingOuter(0.5);

  function getViolinPath(
    scale: ScaleLinear<number, number, never> | ScaleBand<number>,
    densities: { x: number; density: number }[]
  ) {
    // the densities can be really small values that end up getting respresented
    // in scientific notation in the path strings. we want to avoid that.

    const violinHeight = scaleLinear()
      .domain([0, max(densities, (d) => d.density) ?? 0])
      .range([0, yBox.bandwidth() / 2]);

    const violinArea = area<{ x: number; density: number }>()
      .x((d) => scale(d.x) ?? 0)
      .y0((d) => {
        const yCoord = violinHeight(d.density);
        return yCoord > 0.01 ? -yCoord : 0;
      })
      .y1((d) => {
        const yCoord = violinHeight(d.density);
        return yCoord > 0.01 ? yCoord : 0;
      });

    return violinArea(densities);
  }

  function getValueMap(feature: FeatureInfo): Record<number, string> {
    return 'value_map' in feature ? feature.value_map : {};
  }

  function getBarWidth(
    scale: ScaleLinear<number, number, never> | ScaleBand<number>
  ): number {
    if (!scale) {
      return 0;
    }

    return 'bandwidth' in scale ? scale.bandwidth() : 0;
  }

  function getBarX(
    valueOrIndex: number,
    scale: ScaleLinear<number, number, never> | ScaleBand<number>
  ): number {
    if (!scale) {
      return 0;
    }

    return scale(valueOrIndex) ?? 0;
  }

  // interaction

  const brushHeight = 10;
  // map from feature to the brush selection for that feature
  const selectedRanges = new Map<
    string,
    | { kind: 'quantitative'; left: number; right: number }
    | { kind: 'categorical'; categories: number[] }
  >();

  const dispatch = createEventDispatcher<{ filter: number[] }>();

  // guided by https://observablehq.com/@d3/brushable-parallel-coordinates
  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    const feature = this.id.split('-', 2)[1];

    if (selection === null) {
      selectedRanges.delete(feature);
    } else {
      // get the left and right x pixel coordinates of the brush
      const [x1, x2] = selection as [number, number];

      const scale = x[feature];

      if ('bandwidth' in scale) {
        const categories = scale.domain().filter((d) => {
          // get the min and max x values for the category
          const minX = scale(d) ?? 0;
          const maxY = minX + scale.bandwidth();
          return x1 <= maxY && x2 >= minX;
        });
        selectedRanges.set(feature, { kind: 'categorical', categories });
      } else {
        // convert the x coordinates into feature values
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

    dispatch('filter', filteredI);
  }

  $: brush = d3brushX<undefined>()
    .extent([
      [margin.left, -brushHeight / 2 + fy.bandwidth() - margin.bottom],
      [
        visWidth - margin.right,
        brushHeight / 2 + fy.bandwidth() - margin.bottom,
      ],
    ])
    .on('start brush end', brushed);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, SVGElement, undefined>;

  async function setupBrush() {
    // this is needed for when the number of clusters is changed.
    // without it, the features variable is updated before the UI.
    await tick();
    selection = select(group).selectAll('.x-axis');
    selection.call(brush);
    selection.call(brush.clear);
  }

  $: if (group && features) {
    setupBrush();
  }
</script>

<div class="distributions-container">
  <div class="distributions-header">
    <div class="pdpilot-bold">Feature Distributions</div>
    <div class="distributions-settings">
      {#if categoricalFeatures.length > 0}
        <label class="label-and-input">
          <input type="checkbox" bind:checked={normalize} />Normalize bar charts
        </label>
      {/if}
      <div>
        {filteredI.length}
        {filteredI.length === 1 ? 'instance' : 'instances'} selected
      </div>
    </div>
  </div>
  <div class="distribution-plots" bind:this={div}>
    <svg width={visWidth} height={visTotalHeight}>
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
                          x={getBarX(point.data[0], x[d.feature]) + 1}
                          width={getBarWidth(x[d.feature]) - 2}
                          y={yBar(point[1])}
                          height={yBar(point[0]) - yBar(point[1])}
                        />
                      {/if}
                    {/each}
                  </g>
                {/each}
              </g>
              <YAxis
                scale={yBar}
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
                      d={getViolinPath(x[d.feature], box.densities)}
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
            <!-- we need the id so that we can determine which feature the brush is for -->
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
</div>

<style>
  .distributions-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .distributions-header {
    margin-bottom: 0.5em;
  }

  .distributions-settings {
    display: flex;
    align-items: center;
    gap: 1em;
  }

  .distribution-plots {
    flex: 1;
    overflow-y: auto;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }
</style>
