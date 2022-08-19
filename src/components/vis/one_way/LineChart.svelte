<script lang="ts">
  import type {
    QuantitativeMarginalDistribution,
    QuantitativeSinglePDPData,
  } from '../../../types';
  import { scaleLinear } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_prediction_extent } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';

  export let pdp: QuantitativeSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let marginalDistributionX: QuantitativeMarginalDistribution | null;

  // this approach for generating a unique id to use for the
  // clip path comes from https://observablehq.com/@d3/difference-chart

  const clipPathId: string = Math.random().toString(16).slice(2);

  $: margin = {
    top: marginalDistributionX !== null ? 100 : 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: x = scaleLinear()
    .domain([pdp.x_values[0], pdp.x_values[pdp.x_values.length - 1]])
    .range([margin.left, width - margin.right]);

  $: yGlobal = scaleLinear()
    .domain($nice_prediction_extent)
    .range([height - margin.bottom, margin.top]);

  $: yLocal = scaleLinear()
    .domain([pdp.min_prediction, pdp.max_prediction])
    .nice()
    .range([height - margin.bottom, margin.top]);

  $: y = scaleLocally ? yLocal : yGlobal;

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: indices = range(pdp.x_values.length);

  $: pdpLine = d3line<number>()
    .x((i) => x(pdp.x_values[i]))
    .y((i) => y(pdp.mean_predictions[i]));

  $: goodFitTrendLine = d3line<number>()
    .x((i) => x(pdp.x_values[i]))
    .y((i) => y(pdp.trend_good_fit[i]));
</script>

<!--
  setting the width and height in pixels, as with

  <svg width={width} height={height}>

  or

  <svg style="width: {width}; height: {height};">

  was causing issues with resizing.
-->
<svg class="pdp-line-chart">
  <g>
    <clipPath id={clipPathId}>
      <rect
        x={margin.left}
        y={margin.top}
        width={width - margin.left - margin.right}
        height={height - margin.top - margin.bottom}
        fill="white"
      />
    </clipPath>
  </g>

  {#if showTrendLine}
    <path
      class="line"
      d={goodFitTrendLine(indices)}
      stroke="#7C7C7C"
      fill="none"
      stroke-width="2"
      clip-path="url(#{clipPathId})"
    />
  {/if}

  <path
    class="line"
    d={pdpLine(indices)}
    stroke="var(--magenta)"
    stroke-width="2"
    fill="none"
  />

  <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

  <YAxis scale={y} x={margin.left} label={'average prediction'} />

  {#if marginalDistributionX !== null}
    <MarginalHistogram
      data={marginalDistributionX}
      {x}
      height={margin.top}
      direction="horizontal"
    />
  {/if}
</svg>

<style>
  .pdp-line-chart {
    width: 100%;
    height: 100%;
  }

  .line {
    transition: d 150ms;
  }
</style>
