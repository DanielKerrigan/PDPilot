<script lang="ts">
  import {
    scaleLinear,
    scaleBand,
    scaleSequential,
    scaleOrdinal,
  } from 'd3-scale';
  import { interpolatePlasma } from 'd3-scale-chromatic';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { getNiceDomain, scaleCanvas } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { onMount } from 'svelte';
  import {
    feature_info,
    dataset,
    labels,
    isClassification,
    quasiRandomPoints,
  } from '../../../stores';
  import type { TwoWayPD } from '../../../types';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import QuantitativeColorLegend from '../legends/QuantitativeColorLegend.svelte';
  import CategoricalColorLegend from '../legends/CategoricalColorLegend.svelte';
  import { drawScatterplot } from '../../../drawing';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let showMarginalDistribution: boolean;
  export let colorLegendTitle = '';
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

  // color legend centering

  const legendMargin = 10;
  $: legendMarginOffset = colorLegendTitle === '' ? legendMargin : 0;
  $: legendWidthOffset =
    colorLegendTitle === '' ? legendMargin * 2 : legendMargin;

  // if there is extra top bottom margin and we are showing the color legend,
  // then the extra margin will be split between above the chart and above the legend

  $: aboveLegendMargin = extraTopBottomMargin;

  $: margin = {
    top: minMargin.top,
    right: minMargin.right + extraLeftRightMargin,
    bottom: minMargin.bottom + extraTopBottomMargin,
    left: minMargin.left + extraLeftRightMargin,
  };

  // plot data

  $: xFeature = $feature_info[pd.x_feature];
  $: yFeature = $feature_info[pd.y_feature];

  $: xValues = $dataset[pd.x_feature];
  $: yValues = $dataset[pd.y_feature];

  $: heightExcludingLegend = height - legendHeight - aboveLegendMargin;

  // scales

  $: colorAdjust = scaleLinear().domain([0, 1]).range([0.9, 0]);

  $: color = $isClassification
    ? scaleOrdinal<number, string>()
        .domain($labels)
        .range(['#db5c39', '#5c39db'])
    : scaleSequential()
        .domain(getNiceDomain([Math.min(...$labels), Math.max(...$labels)]))
        .interpolator((t: number) => interpolatePlasma(colorAdjust(t)));

  $: x =
    xFeature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_axis[0], pd.x_axis[pd.x_axis.length - 1]])
          .range([margin.left, width - margin.right])
      : scaleBand<number>()
          .domain(pd.x_axis)
          .paddingInner(0.25)
          .range([margin.left, width - margin.right]);

  $: y =
    yFeature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.y_axis[0], pd.y_axis[pd.y_axis.length - 1]])
          .range([heightExcludingLegend - margin.bottom, margin.top])
      : scaleBand<number>()
          .domain(pd.y_axis)
          .paddingInner(0.25)
          .range([heightExcludingLegend - margin.bottom, margin.top]);

  const radius = 2;

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
      yValues,
      $labels,
      $quasiRandomPoints,
      width,
      height,
      radius,
      1
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
    yValues,
    $labels,
    $quasiRandomPoints,
    width,
    height,
    radius,
    1
  );
</script>

<div
  class="two-way-container"
  style:--top="{legendHeight + aboveLegendMargin}px"
>
  <!-- using padding instead of margin to avoid margin collapse -->
  <div
    style:margin-left="{margin.left - legendMarginOffset}px"
    style:padding-top="{aboveLegendMargin}px"
  >
    {#if 'interpolator' in color}
      <QuantitativeColorLegend
        width={sideLength + legendWidthOffset}
        height={legendHeight}
        {color}
        marginLeft={legendMargin}
        marginRight={legendMargin}
        title={colorLegendTitle}
      />
    {:else}
      <CategoricalColorLegend
        width={sideLength + legendWidthOffset}
        height={legendHeight}
        {color}
        marginLeft={legendMargin}
        marginRight={legendMargin}
        title={colorLegendTitle}
      />
    {/if}
  </div>

  <canvas bind:this={canvas} />

  <svg {width} height={heightExcludingLegend}>
    <XAxis
      scale={x}
      y={heightExcludingLegend - margin.bottom}
      label={pd.x_feature}
      integerOnly={xFeature.subkind === 'discrete'}
      value_map={'value_map' in xFeature ? xFeature.value_map : {}}
    />

    <YAxis
      scale={y}
      x={margin.left}
      label={pd.y_feature}
      integerOnly={yFeature.subkind === 'discrete'}
      value_map={'value_map' in yFeature ? yFeature.value_map : {}}
    />

    {#if showMarginalDistribution}
      {#if 'bandwidth' in x}
        <MarginalBarChart
          data={xFeature.distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[
            0,
            margin.top - marginalPlotHeight - (marginTop - marginalPlotHeight),
          ]}
        />
      {:else}
        <MarginalHistogram
          data={xFeature.distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[
            0,
            margin.top - marginalPlotHeight - (marginTop - marginalPlotHeight),
          ]}
        />
      {/if}

      {#if 'bandwidth' in y}
        <MarginalBarChart
          data={yFeature.distribution}
          x={y}
          height={marginalPlotHeight}
          direction="vertical"
          translate={[
            width - margin.right + (marginRight - marginalPlotHeight),
            0,
          ]}
        />
      {:else}
        <MarginalHistogram
          data={yFeature.distribution}
          x={y}
          height={marginalPlotHeight}
          direction="vertical"
          translate={[
            width - margin.right + (marginRight - marginalPlotHeight),
            0,
          ]}
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
