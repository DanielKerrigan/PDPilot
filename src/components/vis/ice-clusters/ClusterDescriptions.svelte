<script lang="ts">
  import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
  import type { ScaleBand, ScaleLinear, ScaleOrdinal } from 'd3-scale';
  import { range, rollup } from 'd3-array';
  import { format } from 'd3-format';
  import {
    stack,
    stackOffsetExpand,
    stackOffsetNone,
    stackOrderReverse,
  } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { FeatureInfo, OneWayPD, RaincloudData } from '../../../types';
  import {
    categoricalColors,
    defaultFormat,
    getRaincloudData,
    scaleCanvas,
  } from '../../../vis-utils';
  import YAxis from '../axis/YAxis.svelte';
  import XAxis from '../axis/XAxis.svelte';
  import { select } from 'd3-selection';
  import { brushX as d3brushX } from 'd3-brush';
  import type { InternMap } from 'd3-array';
  import type { Series } from 'd3-shape';
  import type { Selection } from 'd3-selection';
  import type { D3BrushEvent, BrushBehavior } from 'd3-brush';
  import { createEventDispatcher, onMount, tick } from 'svelte';
  import { getClustering } from '../../../utils';
  import { drawHorizontalRaincloudPlot } from '../../../drawing';

  export let pd: OneWayPD;
  export let features: string[];

  const margin = {
    top: 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  // we don't pass width and height to this component, primarily so that
  // we can take into account the width of the scroll bar on Windows.
  let visWidth = 0;
  let visViewHeight = 0;

  let contentRect: DOMRectReadOnly | undefined | null;
  $: visWidth = contentRect ? contentRect.width : 0;
  $: visViewHeight = contentRect ? contentRect.height : 0;

  let normalize = false;

  // size of the box plot inside of the violin
  const raincloudMinHeight = 30;

  $: visTotalHeight = Math.max(
    visViewHeight,
    features.length *
      (pd.ice.num_clusters * raincloudMinHeight + margin.top + margin.bottom)
  );

  $: cluster_labels = getClustering(pd).cluster_labels;

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
      raincloud: RaincloudData;
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
          const values = group.map((i) => $dataset[f][i]);
          return getRaincloudData(values);
        },
        // group by cluster
        (i) => cluster_labels[i]
      );
      return {
        feature: f,
        kind: 'quantitative',
        data: Array.from(aggregate, ([cluster, raincloud]) => ({
          cluster,
          raincloud,
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

  // y-scale for faceting the raincloud plots by cluster
  $: yRaincloud = scaleBand<number>()
    .domain(clusterIds)
    .range([margin.top, fy.bandwidth() - margin.bottom])
    .paddingInner(0.2)
    .paddingOuter(0.1);

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

  const brushHeight = 8;
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
          const maxX = minX + scale.bandwidth();
          return x1 <= maxX && x2 >= minX;
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

  let group: SVGGElement | undefined;
  let selection:
    | Selection<SVGGElement, undefined, SVGElement, undefined>
    | undefined;

  async function setupBrush(brush: BrushBehavior<undefined>) {
    if (!group) {
      return;
    }
    // this is needed for when the number of clusters is changed.
    // without it, the features variable is updated before the UI.
    await tick();
    selection = select(group).selectAll('.x-axis');
    selection.call(brush);
    selection.call(brush.clear);
  }

  // avoid drawing rect for brush with negative width
  $: if (group && features && visWidth > 0) {
    setupBrush(brush);
  }

  // canvas

  let canvas: HTMLCanvasElement | undefined;
  let ctx: CanvasRenderingContext2D | undefined;

  onMount(() => {
    if (canvas) {
      ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
    }
  });

  function drawAllRaincloudPlots(
    ctx: CanvasRenderingContext2D | undefined,
    x: Record<string, ScaleLinear<number, number> | ScaleBand<number>>,
    featureY: ScaleBand<string>,
    clusterY: ScaleBand<number>,
    color: ScaleOrdinal<number, string>,
    featureData: FeatureData[],
    width: number,
    height: number
  ) {
    if (!ctx) {
      return;
    }

    ctx.save();
    ctx.clearRect(0, 0, width, height);

    featureData.forEach(({ feature, kind, data }) => {
      if (kind === 'categorical') {
        return;
      }

      const xScale = x[feature];
      if ('bandwidth' in xScale) {
        return;
      }

      const featureYCoord = featureY(feature) ?? 0;

      data.forEach(({ cluster, raincloud }) => {
        const clusterYCoord = clusterY(cluster) ?? 0;

        ctx.translate(0, featureYCoord + clusterYCoord);

        drawHorizontalRaincloudPlot(
          raincloud,
          ctx,
          xScale,
          width,
          clusterY.bandwidth(),
          0.5,
          color(cluster),
          'black',
          color(cluster)
        );

        ctx.translate(0, -(featureYCoord + clusterYCoord));
      });
    });

    ctx.restore();
  }

  function draw() {
    drawAllRaincloudPlots(
      ctx,
      x,
      fy,
      yRaincloud,
      color,
      distributions,
      visWidth,
      visTotalHeight
    );
  }

  $: if (canvas && ctx) {
    scaleCanvas(canvas, ctx, visWidth, visTotalHeight);
    draw();
  }

  $: drawAllRaincloudPlots(
    ctx,
    x,
    fy,
    yRaincloud,
    color,
    distributions,
    visWidth,
    visTotalHeight
  );
</script>

<div class="distributions-container">
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
  <!-- TODO: switch to bind:contentBoxSize when it is working -->
  <div class="distribution-plots" bind:contentRect>
    <canvas bind:this={canvas} />

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
    gap: 0.5em;
  }

  .distributions-settings {
    display: flex;
    align-items: center;
    gap: 1em;
  }

  .distribution-plots {
    flex: 1;
    overflow-y: auto;
    position: relative;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  svg,
  canvas {
    position: absolute;
    left: 0;
  }
</style>
