<script lang="ts">
  import { scaleOrdinal, scaleLinear, scaleBand } from 'd3-scale';
  import { range } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    getMaxPercent,
    highlightColor,
    scaleCanvas,
  } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { onMount } from 'svelte';
  import {
    feature_info,
    dataset,
    labels,
    num_instances,
    isClassification,
    highlighted_indices,
    highlightedIndicesSet,
    brushedFeature,
    brushingInProgress,
    highlightedDistributions,
    labelExtent,
    quasiRandomPoints,
  } from '../../../stores';
  import type { Distribution, OneWayPD } from '../../../types';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import type { D3BrushEvent } from 'd3-brush';
  import { brush as d3brush } from 'd3-brush';
  import { select } from 'd3-selection';
  import type { Selection } from 'd3-selection';
  import { drawScatterplot } from '../../../drawing';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let showMarginalDistribution: boolean;
  export let marginTop = 0;
  export let marginRight = 0;
  export let marginalPlotHeight: number;

  let canvas: HTMLCanvasElement | undefined;
  let ctx: CanvasRenderingContext2D | undefined;

  // dimensions and margins

  const legendHeight = 24;

  $: minMargin = {
    top: marginTop,
    right: marginRight,
    bottom: 35,
    left: 50,
  };

  $: sideLength = Math.min(
    width - minMargin.left - minMargin.right,
    height - legendHeight - minMargin.top - minMargin.bottom
  );

  $: extraLeftRightMargin =
    (width - sideLength - minMargin.left - minMargin.right) / 2;

  $: extraTopBottomMargin =
    (height - legendHeight - sideLength - minMargin.top - minMargin.bottom) / 2;

  // if there is extra top bottom margin and we are showing the color legend,
  // then the extra margin will be split between above the chart and above the legend

  $: margin = {
    top: minMargin.top + extraTopBottomMargin,
    right: minMargin.right + extraLeftRightMargin,
    bottom: minMargin.bottom + extraTopBottomMargin,
    left: minMargin.left + extraLeftRightMargin,
  };

  // scales

  $: x =
    feature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_values[0], pd.x_values[pd.x_values.length - 1]])
          .range([margin.left, width - margin.right])
      : scaleBand<number>()
          .domain(pd.x_values)
          .paddingInner(0.25)
          .range([margin.left, width - margin.right]);

  $: y = $isClassification
    ? scaleBand<number>()
        .domain($labelExtent)
        .paddingInner(0.25)
        .range([height - margin.bottom, margin.top])
    : scaleLinear()
        .domain($labelExtent)
        .range([height - margin.bottom, margin.top]);

  $: color = scaleOrdinal<number, string>()
    .domain([0, 1])
    .range(['rgb(145, 145, 145)', highlightColor]);

  const radius = 2;

  // plot data

  $: feature = $feature_info[pd.x_feature];
  $: xValues = $dataset[pd.x_feature];
  $: colorValues = Array.from({ length: $num_instances }, (_, i) =>
    $highlightedIndicesSet.has(i) ? 1 : 0
  );
  $: I = range($num_instances);

  // brushing

  // does the brush for this feature have a selection
  // TODO: can we get rid of this and just use $brushedFeature?
  let activeBrush = false;
  // is the brush for this feature being moved
  let brushingThisFeatureInProgress = false;

  function brushStart(this: SVGGElement, _: D3BrushEvent<undefined>) {
    activeBrush = true;
    $brushingInProgress = true;
    brushingThisFeatureInProgress = true;
  }

  // guided by https://observablehq.com/@d3/brushable-parallel-coordinates
  // and https://observablehq.com/@d3/brushable-scatterplot-matrix
  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (!selection) {
      $highlighted_indices = [];
      return;
    }

    $brushedFeature = pd.x_feature;

    // get the left and right x pixel coordinates of the brush
    const [[x1, y1], [x2, y2]] = selection as [
      [number, number],
      [number, number]
    ];

    if ('bandwidth' in x && 'bandwidth' in y) {
      // categorical scatterplot
      let idx = [];
      for (const i of I) {
        const minX = x(xValues[i]) ?? 0;
        const maxX = minX + x.bandwidth();
        const minY = y($labels[i]) ?? 0;
        const maxY = minY + y.bandwidth();
        if (x1 <= maxX && x2 >= minX && y1 <= maxY && y2 >= minY) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    } else if ('bandwidth' in x && !('bandwidth' in y)) {
      // vertical strip plots
      let idx = [];
      for (const i of I) {
        const minX = x(xValues[i]) ?? 0;
        const maxX = minX + x.bandwidth();
        if (
          x1 <= maxX &&
          x2 >= minX &&
          y($labels[i]) >= y1 &&
          y($labels[i]) <= y2
        ) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    } else if (!('bandwidth' in x) && 'bandwidth' in y) {
      // horizontal strip plots
      let idx = [];
      for (const i of I) {
        const minY = y($labels[i]) ?? 0;
        const maxY = minY + y.bandwidth();
        if (
          x(xValues[i]) >= x1 &&
          x(xValues[i]) <= x2 &&
          y1 <= maxY &&
          y2 >= minY
        ) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    } else if (!('bandwidth' in x || 'bandwidth' in y)) {
      // scatterplot
      let idx = [];
      for (const i of I) {
        if (
          x(xValues[i]) >= x1 &&
          x(xValues[i]) <= x2 &&
          y($labels[i]) >= y1 &&
          y($labels[i]) <= y2
        ) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    }
  }

  function brushEnd(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection === null) {
      activeBrush = false;
      $highlighted_indices = [];
      $brushedFeature = '';
    }

    $brushingInProgress = false;
    brushingThisFeatureInProgress = false;
  }

  $: brush = d3brush<undefined>()
    .extent([
      [margin.left - radius, margin.top - radius],
      [width - margin.right + radius, height - margin.bottom + radius],
    ])
    .on('start', brushStart)
    .on('brush', brushed)
    .on('end', brushEnd);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, null, undefined>;

  // TODO: this won't disable brushing after it's enabled
  $: if (group) {
    selection = select(group);
    selection.call(brush);
  }

  // clear this brush if a plot in the one-way plots tab is brushed
  $: if ($brushingInProgress && activeBrush && !brushingThisFeatureInProgress) {
    selection.call(brush.clear);
  }

  let highlightedDistribution: Distribution | undefined;
  $: highlightedDistribution = $highlightedDistributions.get(pd.x_feature);

  $: showHighlightedDistribution =
    highlightedDistribution && $highlighted_indices.length > 0;

  $: maxPercent = getMaxPercent(feature.distribution, highlightedDistribution);

  // canvas

  onMount(() => {
    if (canvas) {
      ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
    }
  });

  function draw() {
    drawScatterplot(
      ctx,
      x,
      y,
      color,
      xValues,
      $labels,
      colorValues,
      $quasiRandomPoints,
      width,
      height,
      radius,
      0.5
    );
  }

  $: if (canvas && ctx) {
    scaleCanvas(canvas, ctx, width, height);
    draw();
  }

  $: drawScatterplot(
    ctx,
    x,
    y,
    color,
    xValues,
    $labels,
    colorValues,
    $quasiRandomPoints,
    width,
    height,
    radius,
    0.5
  );
</script>

<div class="two-way-container">
  <canvas bind:this={canvas} />

  <svg {width} {height}>
    <XAxis
      scale={x}
      y={height - margin.bottom}
      label={pd.x_feature}
      integerOnly={feature.subkind === 'discrete'}
      value_map={'value_map' in feature ? feature.value_map : {}}
    />

    <YAxis
      scale={y}
      x={margin.left}
      label="Ground truth"
      integerOnly={false}
      value_map={{}}
    />

    <g bind:this={group} />

    {#if showMarginalDistribution}
      {#if highlightedDistribution && $highlighted_indices.length > 0}
        {#if 'bandwidth' in x}
          <MarginalBarChart
            data={highlightedDistribution}
            fill={highlightColor}
            {x}
            height={marginalPlotHeight}
            direction="horizontal"
            translate={[
              0,
              margin.top -
                marginalPlotHeight -
                (marginTop - marginalPlotHeight),
            ]}
            unit="percent"
            maxValue={maxPercent}
          />
        {:else}
          <MarginalHistogram
            data={highlightedDistribution}
            fill={highlightColor}
            {x}
            height={marginalPlotHeight}
            direction="horizontal"
            translate={[
              0,
              margin.top -
                marginalPlotHeight -
                (marginTop - marginalPlotHeight),
            ]}
            unit="percent"
            maxValue={maxPercent}
          />
        {/if}
      {/if}
      {#if 'bandwidth' in x}
        <MarginalBarChart
          data={feature.distribution}
          fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
          stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[
            0,
            margin.top - marginalPlotHeight - (marginTop - marginalPlotHeight),
          ]}
          unit="percent"
          maxValue={maxPercent}
        />
      {:else}
        <MarginalHistogram
          data={feature.distribution}
          fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
          stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[
            0,
            margin.top - marginalPlotHeight - (marginTop - marginalPlotHeight),
          ]}
          unit="percent"
          maxValue={maxPercent}
        />
      {/if}
    {/if}
  </svg>
</div>

<style>
  .two-way-container {
    position: relative;
    width: 100%;
    height: 100%;
  }

  svg,
  canvas {
    position: absolute;
    top: var(--top);
    left: 0;
  }
</style>
