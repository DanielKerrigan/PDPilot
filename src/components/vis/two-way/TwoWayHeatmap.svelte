<script lang="ts">
  import { scaleLinear, scaleBand } from 'd3-scale';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { onMount } from 'svelte';
  import { getHeatmapDiffs, scaleCanvas } from '../../../vis-utils';
  import { drawHeatmap } from '../../../drawing';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import QuantitativeColorLegend from '../legends/QuantitativeColorLegend.svelte';
  import type { TwoWayPD } from '../../../types';
  import {
    feature_info,
    globalColorTwoWayInteraction,
    globalColorTwoWayPdp,
    featureToPd,
  } from '../../../stores';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import MarginalPDP from '../marginal/MarginalPDP.svelte';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let showMarginalPdp: boolean;
  export let colorShows: 'predictions' | 'interactions';
  export let colorLegendTitle = '';
  export let showColorLegend: boolean;
  export let marginTop = 0;
  export let marginRight = 0;
  export let marginalPlotHeight: number;

  $: legendHeight = showColorLegend ? 24 : 0;

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
  // then the extra margin will be above the legend

  $: aboveLegendMargin = showColorLegend ? extraTopBottomMargin : 0;

  $: margin = {
    top: minMargin.top + extraTopBottomMargin - aboveLegendMargin,
    right: minMargin.right + extraLeftRightMargin,
    bottom: minMargin.bottom + extraTopBottomMargin,
    left: minMargin.left + extraLeftRightMargin,
  };

  $: heightExcludingLegend = height - legendHeight - aboveLegendMargin;

  $: xFeature = $feature_info[pd.x_feature];
  $: yFeature = $feature_info[pd.y_feature];

  $: localColorPdp = $globalColorTwoWayPdp
    .copy()
    .domain([pd.pdp_min, pd.pdp_max]);

  $: localColorInteraction = $globalColorTwoWayInteraction
    .copy()
    .domain([pd.interaction_min, 0, pd.interaction_max]);

  $: color =
    colorShows === 'interactions'
      ? scaleLocally
        ? localColorInteraction
        : $globalColorTwoWayInteraction
      : scaleLocally
      ? localColorPdp
      : $globalColorTwoWayPdp;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  // get the differences between sampling points
  $: diffX = getHeatmapDiffs(pd.x_axis);
  $: diffY = getHeatmapDiffs(pd.y_axis);

  $: minX = pd.x_axis[0] - (diffX.get(pd.x_axis[0])?.before ?? 0);
  $: maxX =
    pd.x_axis[pd.x_axis.length - 1] +
    (diffX.get(pd.x_axis[pd.x_axis.length - 1])?.after ?? 0);

  $: minY = pd.y_axis[0] - (diffY.get(pd.y_axis[0])?.before ?? 0);
  $: maxY =
    pd.y_axis[pd.y_axis.length - 1] +
    (diffY.get(pd.y_axis[pd.y_axis.length - 1])?.after ?? 0);

  $: x =
    xFeature.kind === 'quantitative'
      ? scaleLinear()
          .domain([minX, maxX])
          .range([margin.left, width - margin.right])
      : scaleBand<number>()
          .domain(pd.x_axis)
          .range([margin.left, width - margin.right]);

  $: y =
    yFeature.kind === 'quantitative'
      ? scaleLinear()
          .domain([minY, maxY])
          .range([heightExcludingLegend - margin.bottom, margin.top])
      : scaleBand<number>()
          .domain(pd.y_axis)
          .range([heightExcludingLegend - margin.bottom, margin.top]);

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  /*
  If scaleCanvas is called after drawHeatmap, then it will clear the canvas.
  This was happening when changing the sorting order of the PDPs.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pd, x, y, color, or showInteractions.
  */
  function draw() {
    // TODO: are these checks needed?
    if (ctx && x !== null && x !== undefined && y !== null && y !== undefined) {
      drawHeatmap(
        pd,
        ctx,
        width,
        heightExcludingLegend,
        x,
        y,
        color,
        colorShows,
        diffX,
        diffY
      );
    }
  }
  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, heightExcludingLegend);
    draw();
  }

  $: if (
    ctx &&
    x !== null &&
    x !== undefined &&
    y !== null &&
    y !== undefined
  ) {
    drawHeatmap(
      pd,
      ctx,
      width,
      heightExcludingLegend,
      x,
      y,
      color,
      colorShows,
      diffX,
      diffY
    );
  }

  // color legend centering

  const legendMargin = 10;
  $: legendMarginOffset = colorLegendTitle === '' ? legendMargin : 0;
  $: legendWidthOffset =
    colorLegendTitle === '' ? legendMargin * 2 : legendMargin;

  // one way pds

  $: xPdp = $featureToPd.get(pd.x_feature);
  $: yPdp = $featureToPd.get(pd.y_feature);
</script>

<div
  class="two-way-container"
  style:--top="{legendHeight + aboveLegendMargin}px"
>
  {#if showColorLegend}
    <!-- using padding instead of margin to avoid margin collapse -->
    <div
      style:margin-left="{margin.left - legendMarginOffset}px"
      style:padding-top="{aboveLegendMargin}px"
    >
      <QuantitativeColorLegend
        width={sideLength + legendWidthOffset}
        height={legendHeight}
        {color}
        marginLeft={legendMargin}
        marginRight={legendMargin}
        title={colorLegendTitle}
      />
    </div>
  {/if}

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
          translate={[0, margin.top - marginalPlotHeight]}
        />
      {:else}
        <MarginalHistogram
          data={xFeature.distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[0, margin.top - marginalPlotHeight]}
        />
      {/if}

      {#if 'bandwidth' in y}
        <MarginalBarChart
          data={yFeature.distribution}
          x={y}
          height={marginalPlotHeight}
          direction="vertical"
          translate={[width - margin.right, 0]}
        />
      {:else}
        <MarginalHistogram
          data={yFeature.distribution}
          x={y}
          height={marginalPlotHeight}
          direction="vertical"
          translate={[width - margin.right, 0]}
        />
      {/if}
    {:else if showMarginalPdp && xPdp && yPdp}
      <MarginalPDP
        pd={xPdp}
        height={marginalPlotHeight}
        direction="horizontal"
        {x}
        translate={[0, margin.top - marginalPlotHeight]}
      />

      <MarginalPDP
        pd={yPdp}
        height={marginalPlotHeight}
        direction="vertical"
        x={y}
        translate={[width - margin.right, 0]}
      />
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
