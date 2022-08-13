<script lang="ts">
  import type {
    CategoricalSinglePDPData,
    CategoricalMarginalDistribution,
  } from '../../../types';
  import { scalePoint, scaleLinear } from 'd3-scale';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_prediction_extent } from '../../../stores';
  import { range } from 'd3-array';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let marginalDistributionX: CategoricalMarginalDistribution | null;

  $: margin = {
    top: marginalDistributionX !== null ? 100 : 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: x = scalePoint<string | number>()
    .domain(pdp.x_values)
    .range([margin.left, width - margin.right])
    .padding(0.5);

  $: yGlobal = scaleLinear()
    .domain($nice_prediction_extent)
    .range([height - margin.bottom, margin.top]);

  $: yLocal = scaleLinear()
    .domain([pdp.min_prediction, pdp.max_prediction])
    .nice()
    .range([height - margin.bottom, margin.top]);

  $: y = scaleLocally ? yLocal : yGlobal;

  $: radius = Math.min(3, x.step() / 2 - 1);

  $: indices = range(pdp.x_values.length);
</script>

<svg class="pdp-dot-plot">
  <g>
    {#each indices as i}
      <circle
        class="dot"
        cx={x(pdp.x_values[i])}
        cy={y(pdp.mean_predictions[i])}
        r={radius}
        fill="var(--magenta)"
      />
    {/each}
  </g>

  <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

  <YAxis scale={y} x={margin.left} label={'average prediction'} />

  {#if marginalDistributionX !== null}
    <MarginalBarChart
      data={marginalDistributionX}
      {x}
      height={margin.top}
      direction="horizontal"
    />
  {/if}
</svg>

<style>
  .pdp-dot-plot {
    width: 100%;
    height: 100%;
  }

  .dot {
    transition: cx 150ms, cy 150ms;
  }
</style>
