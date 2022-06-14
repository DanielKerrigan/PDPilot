<!--
   References code from: https://observablehq.com/@d3/color-legend
   Copyright 2021, Observable Inc.
   Released under the ISC license.
 -->

 <script lang="ts">
  import * as d3 from 'd3';
  import { onMount } from 'svelte';
import { scaleCanvas } from '../VisUtils';

  export let width: number;
  export let height: number;
  export let color: d3.ScaleSequential<string, string>;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  let format = d3.format('~s');

  // dimensions

  const margin = { top: 4, right: 10, bottom: 2, left: 10 };
  const spaceBetweenColorAndTick = 2;
  const tickHeight = 10;

  $: colorWidth = width - margin.left - margin.right;
  $: colorHeight = height - margin.top - margin.bottom - tickHeight - spaceBetweenColorAndTick;

  // set up

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  // drawing

  function drawRegressionColorScale(
    ctx: CanvasRenderingContext2D,
    interpolator: (t: number) => string,
    colorWidth: number,
    colorHeight: number,
    margin: { top: number, right: number, bottom: number, left: number },
  ) {
    for (let i = 0; i < colorWidth; i++) {
      ctx.fillStyle = interpolator(i / width);
      ctx.fillRect(i + margin.left, margin.top, 1, colorHeight);
    }
  }

  $: if (ctx) scaleCanvas(canvas, ctx, width, height);
  $: if (ctx) drawRegressionColorScale(ctx, color.interpolator(), colorWidth, colorHeight, margin);

  $: x = d3.scaleLinear()
      .domain(color.domain())
      .range([margin.left, width - margin.right]);

  $: ticks = x.ticks(colorWidth / 60);
</script>

<div style="height: {height}px;">
  <canvas bind:this={canvas}/>
  <svg {width} {height}>
    {#each ticks as tick}
      <g transform="translate({x(tick)},{margin.top})">
        <line y1={0} y2={colorHeight} stroke="black"/>
        <text
          y={colorHeight + spaceBetweenColorAndTick}
          dominant-baseline="hanging"
          text-anchor="middle"
          font-size={tickHeight}
        >
          {format(tick)}
        </text>
      </g>
    {/each}
  </svg>
</div>

<style>
  div {
    position: relative;
  }

  svg {
    position: absolute;
    left: 0;
    top: 0;
  }
</style>
