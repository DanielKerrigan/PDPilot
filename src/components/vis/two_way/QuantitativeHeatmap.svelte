<script lang="ts">
  import type {
    QuantitativeDoublePDPData,
    QuantitativeMarginalDistribution,
  } from '../../../types';
  import { scaleLinear, scaleDiverging } from 'd3-scale';
  import { interpolateBrBG } from 'd3-scale-chromatic';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { onMount } from 'svelte';
  import { scaleCanvas } from '../../../vis-utils';
  import { drawQuantitativeHeatmap } from '../../../drawing';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import QuantitativeColorLegend from './QuantitativeColorLegend.svelte';
  import { pairs } from 'd3-array';

  export let pdp: QuantitativeDoublePDPData;
  export let width: number;
  export let height: number;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let scaleLocally: boolean;
  export let marginalDistributionX: QuantitativeMarginalDistribution | null;
  export let marginalDistributionY: QuantitativeMarginalDistribution | null;
  export let showInteractions: boolean;
  export let showColorLegend: boolean;

  $: localColor = globalColor.copy().domain([pdp.pdp_min, pdp.pdp_max]);

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

  // get the minimum difference between sampling points
  $: minDiffX = Math.min(...pairs(pdp.x_axis, (a, b) => b - a));
  $: minDiffY = Math.min(...pairs(pdp.y_axis, (a, b) => b - a));

  $: minX = pdp.x_axis[0] - minDiffX / 2;
  $: maxX = pdp.x_axis[pdp.x_axis.length - 1] + minDiffX / 2;

  $: x = scaleLinear()
    .domain([minX, maxX])
    .range([margin.left, width - margin.right]);

  $: minY = pdp.y_axis[0] - minDiffY / 2;
  $: maxY = pdp.y_axis[pdp.y_axis.length - 1] + minDiffY / 2;

  $: y = scaleLinear()
    .domain([minY, maxY])
    .range([pdpHeight - margin.bottom, margin.top]);

  $: rectWidth = x(minX + minDiffX) - x(minX);
  $: rectHeight = y(minY) - y(minY + minDiffY);

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  /*
  If scaleCanvas is called after drawQuantitativeHeatmap, then it will clear the canvas.
  This was happening when changing the sorting order of the PDPs.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pdp, x, y, color, or showInteractions.
  */
  function draw() {
    if (ctx && x != null && y != null) {
      drawQuantitativeHeatmap(
        pdp,
        ctx,
        width,
        pdpHeight,
        x,
        y,
        color,
        showInteractions,
        rectWidth,
        rectHeight
      );
    }
  }
  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, pdpHeight);
    draw();
  }

  $: if (ctx && x != null && y != null) {
    drawQuantitativeHeatmap(
      pdp,
      ctx,
      width,
      pdpHeight,
      x,
      y,
      color,
      showInteractions,
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

      <MarginalHistogram
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
