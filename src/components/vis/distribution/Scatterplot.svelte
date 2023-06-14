<script lang="ts">
  import {
    scaleLinear,
    scaleBand,
    scaleOrdinal,
    scaleSequential,
  } from 'd3-scale';
  import { interpolatePlasma } from 'd3-scale-chromatic';
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
    highlighted_indices,
    brushedFeature,
    brushingInProgress,
    highlightedDistributions,
    quasiRandomPoints,
  } from '../../../stores';
  import type { Distribution } from '../../../types';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import type { D3BrushEvent } from 'd3-brush';
  import { brush as d3brush } from 'd3-brush';
  import { select } from 'd3-selection';
  import type { Selection } from 'd3-selection';
  import { drawScatterplot } from '../../../drawing';
  import QuantitativeColorLegend from '../legends/QuantitativeColorLegend.svelte';
  import CategoricalColorLegend from '../legends/CategoricalColorLegend.svelte';

  export let width: number;
  export let height: number;
  export let xValues: number[];
  export let yValues: number[];
  export let colorValues: number[];
  export let xKind: 'categorical' | 'quantitative';
  export let yKind: 'categorical' | 'quantitative';
  export let colorKind: 'categorical' | 'quantitative';
  export let xDomain: number[];
  export let yDomain: number[];
  export let colorDomain: number[];
  export let colorScheme: 'highlight' | 'classes' | 'sequential';
  export let xLabel: string;
  export let yLabel: string;
  export let colorLabel: string;
  export let xAxisIntegerOnly: boolean;
  export let yAxisIntegerOnly: boolean;
  export let xAxisValueMap: Record<number, string> | undefined;
  export let yAxisValueMap: Record<number, string> | undefined;
  export let xDistribution: Distribution | null = null;
  export let yDistribution: Distribution | null = null;
  export let opacity = 1;
  export let allowBrushing = false;
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

  // color legend centering

  const legendMargin = 10;
  $: legendMarginOffset = colorLabel === '' ? legendMargin : 0;
  $: legendWidthOffset = colorLabel === '' ? legendMargin * 2 : legendMargin;

  // if there is extra top bottom margin and we are showing the color legend,
  // then the extra margin will be split between above the chart and above the legend

  $: aboveLegendMargin = colorLabel !== '' ? extraTopBottomMargin : 0;

  $: margin = {
    top: minMargin.top + extraTopBottomMargin - aboveLegendMargin,
    right: minMargin.right + extraLeftRightMargin,
    bottom: minMargin.bottom + extraTopBottomMargin,
    left: minMargin.left + extraLeftRightMargin,
  };

  $: heightExcludingLegend = Math.max(
    height - legendHeight - aboveLegendMargin,
    0
  );

  // scales

  $: x =
    xKind === 'quantitative'
      ? scaleLinear()
          .domain(xDomain)
          .range([margin.left, width - margin.right])
      : scaleBand<number>()
          .domain(xDomain)
          .paddingInner(0.25)
          .range([margin.left, width - margin.right]);

  $: y =
    yKind === 'quantitative'
      ? scaleLinear()
          .domain(yDomain)
          .range([heightExcludingLegend - margin.bottom, margin.top])
      : scaleBand<number>()
          .domain(yDomain)
          .paddingInner(0.25)
          .range([heightExcludingLegend - margin.bottom, margin.top]);

  const colorAdjust = scaleLinear().domain([0, 1]).range([0.9, 0]);

  $: color =
    colorKind === 'quantitative'
      ? scaleSequential()
          .domain(colorDomain)
          .interpolator((t: number) => interpolatePlasma(colorAdjust(t)))
      : scaleOrdinal<number, string>()
          .domain(colorDomain)
          .range(
            colorScheme === 'highlight'
              ? ['rgb(145, 145, 145)', highlightColor]
              : ['#db5c39', '#5c39db']
          );

  const radius = 2;

  // plot data

  $: I = range(xValues.length);

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

    $brushedFeature = xLabel;

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
        const minY = y(yValues[i]) ?? 0;
        const maxY = minY + y.bandwidth();
        if (x1 <= maxX && x2 >= minX && y1 <= maxY && y2 >= minY) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    } else if ('bandwidth' in x && !('bandwidth' in y)) {
      // vertical strip plots or violin plots
      let idx = [];
      for (const i of I) {
        const minX = x(xValues[i]) ?? 0;
        const maxX = minX + x.bandwidth();
        if (
          x1 <= maxX &&
          x2 >= minX &&
          y(yValues[i]) >= y1 &&
          y(yValues[i]) <= y2
        ) {
          idx.push(i);
        }
      }
      $highlighted_indices = idx;
    } else if (!('bandwidth' in x) && 'bandwidth' in y) {
      // horizontal strip plots or violin plots
      let idx = [];
      for (const i of I) {
        const minY = y(yValues[i]) ?? 0;
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
          y(yValues[i]) >= y1 &&
          y(yValues[i]) <= y2
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
      [
        width - margin.right + radius,
        heightExcludingLegend - margin.bottom + radius,
      ],
    ])
    .on('start', brushStart)
    .on('brush', brushed)
    .on('end', brushEnd);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, null, undefined> | undefined;

  // don't draw brush with negative dimensions
  $: if (group && allowBrushing && width > 0 && heightExcludingLegend > 0) {
    selection = select(group);
    selection.call(brush);
  }

  // clear this brush if a plot in the one-way plots tab is brushed
  $: if (
    selection &&
    $brushingInProgress &&
    activeBrush &&
    !brushingThisFeatureInProgress
  ) {
    selection.call(brush.clear);
  }

  let highlightedDistribution: Distribution | undefined;
  $: highlightedDistribution = allowBrushing
    ? $highlightedDistributions.get(xLabel)
    : undefined;

  $: showHighlightedDistribution =
    highlightedDistribution && $highlighted_indices.length > 0;

  $: maxPercent = xDistribution
    ? getMaxPercent(xDistribution, highlightedDistribution)
    : 0;

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
      colorValues,
      $quasiRandomPoints,
      width,
      heightExcludingLegend,
      radius,
      opacity
    );
  }

  $: if (canvas && ctx) {
    scaleCanvas(canvas, ctx, width, heightExcludingLegend);
    draw();
  }

  $: drawScatterplot(
    ctx,
    x,
    y,
    color,
    xValues,
    yValues,
    colorValues,
    $quasiRandomPoints,
    width,
    heightExcludingLegend,
    radius,
    opacity
  );
</script>

<div
  class="pdpilot-plot-container"
  style:--top="{legendHeight + aboveLegendMargin}px"
>
  {#if colorLabel !== ''}
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
          title={colorLabel}
        />
      {:else}
        <CategoricalColorLegend
          width={sideLength + legendWidthOffset}
          height={legendHeight}
          {color}
          marginLeft={legendMargin}
          marginRight={legendMargin}
          title={colorLabel}
        />
      {/if}
    </div>
  {/if}

  <canvas bind:this={canvas} />

  <svg {width} height={heightExcludingLegend}>
    <XAxis
      scale={x}
      y={heightExcludingLegend - margin.bottom}
      label={xLabel}
      integerOnly={xAxisIntegerOnly}
      value_map={xAxisValueMap}
    />

    <YAxis
      scale={y}
      x={margin.left}
      label={yLabel}
      integerOnly={yAxisIntegerOnly}
      value_map={yAxisValueMap}
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
      {#if xDistribution}
        {#if 'bandwidth' in x}
          <MarginalBarChart
            data={xDistribution}
            fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
            stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
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
            data={xDistribution}
            fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
            stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
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

      {#if yDistribution}
        {#if 'bandwidth' in y}
          <MarginalBarChart
            data={yDistribution}
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
            data={yDistribution}
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
    {/if}
  </svg>
</div>

<style>
  .pdpilot-plot-container {
    width: 100%;
    height: 100%;
    position: relative;
  }

  svg,
  canvas {
    position: absolute;
    top: var(--top);
    left: 0;
  }
</style>
