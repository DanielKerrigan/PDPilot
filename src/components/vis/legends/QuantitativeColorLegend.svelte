<!--
   References code from: https://observablehq.com/@d3/color-legend
   Copyright 2021, Observable Inc.
   Released under the ISC license.
 -->
<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import type { ScaleSequential, ScaleDiverging } from 'd3-scale';
  import { onMount } from 'svelte';
  import { defaultFormat, scaleCanvas } from '../../../vis-utils';

  export let width: number;
  export let height: number;
  export let color:
    | ScaleSequential<string, string>
    | ScaleDiverging<string, string>;
  export let marginRight = 0;
  export let marginLeft = 0;
  export let title = '';

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  // dimensions

  let nonTitleWidth = 0;

  let borderBoxSize: ResizeObserverSize[] | undefined | null;
  $: nonTitleWidth = borderBoxSize ? borderBoxSize[0].inlineSize : 0;

  $: colorWidth = nonTitleWidth - marginLeft - marginRight;

  const spaceBetweenColorAndTickLabel = 2;
  const tickLabelHeight = 10;

  $: colorHeight = height - tickLabelHeight - spaceBetweenColorAndTickLabel;

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
    marginLeft: number
  ) {
    ctx.clearRect(0, 0, totalWidth, totalHeight);
    for (let i = 0; i < colorWidth; i++) {
      ctx.fillStyle = interpolator(i / colorWidth);
      ctx.fillRect(i + marginLeft, 0, 1, colorHeight);
    }
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, nonTitleWidth, height);
  }
  $: if (ctx) {
    drawRegressionColorScale(
      ctx,
      color.interpolator(),
      width,
      height,
      colorWidth,
      colorHeight,
      marginLeft
    );
  }

  $: x = scaleLinear()
    .domain([color.domain()[0], color.domain()[color.domain().length - 1]])
    .range([marginLeft, nonTitleWidth - marginRight]);

  $: minDesiredTicks = color.domain().length;

  $: ticks = x.ticks(Math.max(Math.min(colorWidth / 50, 10), minDesiredTicks));
</script>

<div
  class="color-container"
  style:height="{height}px"
  style:max-width="{width}px"
>
  {#if title !== ''}
    <div class="pdpilot-small pdpilot-bold">{title}:</div>
  {/if}
  <div class="color-ramp" bind:borderBoxSize>
    <canvas bind:this={canvas} />
    <svg width={nonTitleWidth} {height}>
      {#each ticks as tick}
        <g transform="translate({x(tick)})">
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
  .color-container {
    display: flex;
    align-items: center;
  }

  .color-ramp {
    position: relative;
    flex: 1;
    min-width: 0;
  }

  svg {
    position: absolute;
    left: 0;
    top: 0;
  }
</style>
