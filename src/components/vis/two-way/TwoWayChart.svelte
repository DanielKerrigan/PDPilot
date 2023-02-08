<script lang="ts">
  import { scaleLinear, scaleBand } from 'd3-scale';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { onMount } from 'svelte';
  import { scaleCanvas } from '../../../vis-utils';
  import { drawHeatmap } from '../../../drawing';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import QuantitativeColorLegend from './QuantitativeColorLegend.svelte';
  import { pairs } from 'd3-array';
  import type { TwoWayPD } from '../../../types';
  import {
    feature_info,
    globalColorTwoWayInteraction,
    globalColorTwoWayPdp,
  } from '../../../stores';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let colorShows: 'predictions' | 'interactions';
  export let showColorLegend: boolean;
  export let marginTop = 0;
  export let marginRight = 0;

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

  $: legendHeight = showColorLegend ? 24 : 0;
  $: pdpHeight = height - legendHeight;

  $: margin = {
    top: marginTop,
    right: marginRight,
    bottom: 35,
    left: 50,
  };

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  // get the minimum difference between sampling points
  $: minDiffX = Math.min(...pairs(pd.x_axis, (a, b) => b - a));
  $: minDiffY = Math.min(...pairs(pd.y_axis, (a, b) => b - a));

  $: minX = pd.x_axis[0] - minDiffX / 2;
  $: maxX = pd.x_axis[pd.x_axis.length - 1] + minDiffX / 2;

  $: minY = pd.y_axis[0] - minDiffY / 2;
  $: maxY = pd.y_axis[pd.y_axis.length - 1] + minDiffY / 2;

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
          .range([pdpHeight - margin.bottom, margin.top])
      : scaleBand<number>()
          .domain(pd.y_axis)
          .range([pdpHeight - margin.bottom, margin.top]);

  $: rectWidth =
    'bandwidth' in x ? x.bandwidth() - 2 : x(minX + minDiffX) - x(minX);
  $: rectHeight =
    'bandwidth' in y ? y.bandwidth() - 2 : y(minY) - y(minY + minDiffY);

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
        pdpHeight,
        x,
        y,
        color,
        colorShows,
        rectWidth,
        rectHeight
      );
    }
  }
  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, pdpHeight);
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
      pdpHeight,
      x,
      y,
      color,
      colorShows,
      rectWidth,
      rectHeight
    );
  }
</script>

<div style:--top={legendHeight}>
  {#if showColorLegend}
    <QuantitativeColorLegend
      {width}
      height={legendHeight}
      {color}
      marginLeft={margin.left}
      marginRight={margin.right}
    />
  {/if}

  <canvas bind:this={canvas} />

  <svg {width} height={pdpHeight}>
    <XAxis
      scale={x}
      y={pdpHeight - margin.bottom}
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
          height={margin.top}
          direction="horizontal"
        />
      {:else}
        <MarginalHistogram
          data={xFeature.distribution}
          {x}
          height={margin.top}
          direction="horizontal"
        />
      {/if}

      {#if 'bandwidth' in y}
        <MarginalBarChart
          data={yFeature.distribution}
          x={y}
          height={margin.top}
          direction="vertical"
          translate={[width - margin.right, 0]}
        />
      {:else}
        <MarginalHistogram
          data={yFeature.distribution}
          x={y}
          height={margin.top}
          direction="vertical"
          translate={[width - margin.right, 0]}
        />
      {/if}
    {/if}
  </svg>
</div>

<style>
  div {
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
