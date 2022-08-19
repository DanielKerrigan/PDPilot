<script lang="ts">
  import type {
    CategoricalMarginalDistribution,
    MixedDoublePDPData,
    QuantitativeMarginalDistribution,
  } from '../../../types';
  import { scaleLinear, scaleBand, scaleDiverging } from 'd3-scale';
  import { interpolateBrBG } from 'd3-scale-chromatic';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { onMount } from 'svelte';
  import { scaleCanvas } from '../../../vis-utils';
  import { drawMixedHeatmap } from '../../../drawing';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import QuantitativeColorLegend from './QuantitativeColorLegend.svelte';

  export let pdp: MixedDoublePDPData;
  export let width: number;
  export let height: number;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let scaleLocally: boolean;
  export let marginalDistributionX: QuantitativeMarginalDistribution | null;
  export let marginalDistributionY: CategoricalMarginalDistribution | null;
  export let showInteractions: boolean;
  export let showColorLegend: boolean;

  $: localColor = globalColor
    .copy()
    .domain([pdp.min_prediction, pdp.max_prediction]);

  $: interactionMaxAbs = Math.max(
    Math.abs(Math.min(...pdp.interactions)),
    Math.abs(Math.max(...pdp.interactions))
  );

  $: interactionsColor = scaleDiverging<string, string>()
    .domain([-interactionMaxAbs, 0, interactionMaxAbs])
    .interpolator(interpolateBrBG)
    .unknown('black');

  $: color = showInteractions
    ? interactionsColor
    : scaleLocally
    ? localColor
    : globalColor;

  $: legendHeight = showColorLegend ? 24 : 0;
  $: pdpHeight = height - legendHeight;

  $: margin = {
    top:
      marginalDistributionX !== null && marginalDistributionY !== null
        ? 100
        : showColorLegend
        ? 0
        : 5,
    right:
      marginalDistributionX !== null && marginalDistributionY !== null
        ? 100
        : 15,
    bottom: 35,
    left: 50,
  };

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: x = scaleLinear()
    .domain([pdp.x_axis[0], pdp.x_axis[pdp.x_axis.length - 1]])
    .range([margin.left, width - margin.right]);

  $: y = scaleBand<string | number>()
    .domain(pdp.y_axis)
    .range([pdpHeight - margin.bottom, margin.top]);

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  /*
  If scaleCanvas is called after drawMixedHeatmap, then it will clear the canvas.
  This was happening when changing the sorting order of the PDPs.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pdp, x, y, color, or showInteractions.
  */
  function draw() {
    if (ctx && x != null && y != null) {
      drawMixedHeatmap(pdp, ctx, width, pdpHeight, x, y, color, showInteractions);
    }
  }
  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, pdpHeight);
    draw();
  }

  $: if (ctx && x != null && y != null) {
    drawMixedHeatmap(pdp, ctx, width, pdpHeight, x, y, color, showInteractions);
  }
</script>

<div style:--top={legendHeight}>
  {#if showColorLegend}
    <QuantitativeColorLegend
      {width}
      height={legendHeight}
      {color}
      includeTitle={false}
      marginLeft={margin.left}
      marginRight={margin.right}
    />
  {/if}

  <canvas bind:this={canvas} />

  <svg {width} height={pdpHeight}>
    <XAxis scale={x} y={pdpHeight - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={pdp.y_feature} />

    {#if marginalDistributionX !== null && marginalDistributionY !== null}
      <MarginalHistogram
        data={marginalDistributionX}
        {x}
        height={margin.top}
        direction="horizontal"
      />

      <MarginalBarChart
        data={marginalDistributionY}
        x={y}
        height={margin.right}
        direction="vertical"
        translate={[width - margin.right, 0]}
      />
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
