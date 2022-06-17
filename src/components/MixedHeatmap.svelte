<script lang="ts">
  import type {MixedDoublePDPData} from '../types';
  import * as d3 from 'd3';
  import XAxis from './XAxis.svelte';
  import YAxis from './YAxis.svelte';
  import { onMount } from 'svelte';
  import { scaleCanvas } from '../VisUtils';
  import { drawMixedHeatmap } from '../CanvasDrawing';

  export let pdp: MixedDoublePDPData;
  export let width: number;
  export let height: number;
  export let color: d3.ScaleSequential<string, string>;

  const margin = { top: 5, right: 15, bottom: 35, left: 50 };

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: x = d3.scaleLinear()
    .domain(d3.extent(pdp.values, d => d.x) as [number, number])
    .range([margin.left, width - margin.right]);

  $: y = d3.scaleBand<string|number>()
    .domain(pdp.y_axis)
    .range([height - margin.bottom, margin.top]);

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  $: if (ctx) scaleCanvas(canvas, ctx, width, height);
  $: if (ctx && x !== undefined && y !== undefined) drawMixedHeatmap(pdp, ctx, width, height, x, y, color);
</script>

<div>
  <canvas bind:this={canvas}></canvas>
  <svg width={width} height={height}>
    <XAxis
      scale={x}
      y={height - margin.bottom}
      label={pdp.x_feature}
    />

    <YAxis
      scale={y}
      x={margin.left}
      label={pdp.y_feature}
    />
  </svg>
</div>

<style>
  div {
    position: relative;
    width: 100%;
    height: 100%;
  }

  canvas {
    position: absolute;
    top: 0;
    left: 0;
  }

  svg {
    position: absolute;
    top: 0;
    left: 0;
  }
</style>