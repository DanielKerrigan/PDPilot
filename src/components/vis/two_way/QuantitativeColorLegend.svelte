<!--
   References code from: https://observablehq.com/@d3/color-legend
   Copyright 2021, Observable Inc.
   Released under the ISC license.
 -->
<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import { onMount } from 'svelte';
  import { defaultFormat, scaleCanvas } from '../../../vis-utils';

  export let width: number;
  export let height: number;
  export let color:
    | d3.ScaleSequential<string, string>
    | d3.ScaleDiverging<string, string>;
  export let includeTitle: boolean;

  export let marginTop: number = 0;
  export let marginRight: number = 0;
  export let marginBottom: number = 0;
  export let marginLeft: number = 0;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  // dimensions

  const spaceBetweenColorAndTickLabel = 2;
  const tickLabelHeight = 10;

  $: colorWidth = width - marginLeft - marginRight;
  $: colorHeight =
    height -
    marginTop -
    marginBottom -
    tickLabelHeight -
    spaceBetweenColorAndTickLabel;

  // set up

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  // drawing

  function drawRegressionColorScale(
    ctx: CanvasRenderingContext2D,
    interpolator: (t: number) => string,
    totalWidth: number,
    totalHeight: number,
    colorWidth: number,
    colorHeight: number,
    marginLeft: number,
    marginTop: number
  ) {
    ctx.clearRect(0, 0, totalWidth, totalHeight);
    for (let i = 0; i < colorWidth; i++) {
      ctx.fillStyle = interpolator(i / colorWidth);
      ctx.fillRect(i + marginLeft, marginTop, 1, colorHeight);
    }
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, height);
  }
  $: if (ctx) {
    drawRegressionColorScale(
      ctx,
      color.interpolator(),
      width,
      height,
      colorWidth,
      colorHeight,
      marginLeft,
      marginTop
    );
  }

  $: x = scaleLinear()
    .domain([color.domain()[0], color.domain()[color.domain().length - 1]])
    .range([marginLeft, width - marginRight]);

  $: ticks = x.ticks(colorWidth / 60);
</script>

<div class="legend-container">
  {#if includeTitle}
    <div class="legend-title">Prediction</div>
  {/if}
  <div class="color-container" style="height: {height}px;">
    <canvas bind:this={canvas} />
    <svg {width} {height}>
      {#each ticks as tick}
        <g transform="translate({x(tick)},{marginTop})">
          <line y1={0} y2={colorHeight} stroke="black" />
          <text
            y={colorHeight + spaceBetweenColorAndTickLabel}
            dominant-baseline="hanging"
            text-anchor="middle"
            font-size={tickLabelHeight}
          >
            {defaultFormat(tick)}
          </text>
        </g>
      {/each}
    </svg>
  </div>
</div>

<style>
  .legend-container {
    display: flex;
    align-items: center;
  }

  .color-container {
    position: relative;
  }

  svg {
    position: absolute;
    left: 0;
    top: 0;
  }
</style>
