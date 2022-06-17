<script lang="ts">
  import type { QuantitativeSinglePDPData } from '../types';
  import { scaleLinear } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { extent } from 'd3-array';
  import XAxis from './XAxis.svelte';
  import YAxis from './YAxis.svelte';

  export let pdp: QuantitativeSinglePDPData;
  export let width: number;
  export let height: number;
  export let predictionExtent: [number, number];

  const margin = { top: 10, right: 10, bottom: 40, left: 50 };

  $: x = scaleLinear()
    .domain(extent(pdp.values, (d) => d.x) as [number, number])
    .range([margin.left, width - margin.right]);

  $: y = scaleLinear()
    .domain(predictionExtent)
    .range([height - margin.bottom, margin.top]);

  $: line = d3line<{ x: number; avg_pred: number }>()
    .x((d) => x(d.x))
    .y((d) => y(d.avg_pred));
</script>

<!--
  setting the width and height in pixels, as with

  <svg width={width} height={height}>

  or

  <svg style="width: {width}; height: {height};">

  was causing issues with resizing.
-->
<svg class="pdp-line-chart">
  <path d={line(pdp.values)} stroke="steelblue" fill="none" />

  <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

  <YAxis scale={y} x={margin.left} label={'average prediction'} />
</svg>

<style>
  .pdp-line-chart {
    width: 100%;
    height: 100%;
  }
</style>
