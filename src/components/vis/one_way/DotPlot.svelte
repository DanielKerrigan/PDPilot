<script lang="ts">
  import type {
    CategoricalSinglePDPData,
    CategoricalMarginalDistribution,
  } from '../../../types';
  import { scalePoint, scaleLinear } from 'd3-scale';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_pdp_extent, nice_ice_extent } from '../../../stores';
  import { line } from 'd3-shape';
  import { range } from 'd3-array';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let numIceInstances: number;
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
    .domain(numIceInstances > 0 ? $nice_ice_extent : $nice_pdp_extent)
    .range([height - margin.bottom, margin.top]);

  $: yLocal = scaleLinear()
    .domain(
      numIceInstances > 0
        ? [pdp.ice_min, pdp.ice_max]
        : [pdp.pdp_min, pdp.pdp_max]
    )
    .nice()
    .range([height - margin.bottom, margin.top]);

  $: y = scaleLocally ? yLocal : yGlobal;

  $: radius = Math.min(3, x.step() / 2 - 1);

  $: indices = range(pdp.x_values.length);

  // when there are ICE plots, use lines instead of dots
  $: pdpLine = line<number>()
    .x((i) => x(pdp.x_values[i]) ?? 0)
    .y((i) => y(pdp.mean_predictions[i]));

  $: iceLine = line<number>()
    .x((_, i) => x(pdp.x_values[i]) ?? 0)
    .y((d) => y(d));
</script>

<svg class="pdp-dot-plot">
  <!-- ICE -->
  <g>
    {#each pdp.ice_lines.slice(0, numIceInstances) as ice}
      <path
        d={iceLine(ice)}
        stroke="var(--gray-3)"
        fill="none"
        stroke-opacity="0.4"
        stroke-width="1"
      />
    {/each}
  </g>

  <!-- PDP -->
  <g>
    {#if numIceInstances > 0}
      <path
        d={pdpLine(indices)}
        stroke="var(--magenta)"
        fill="none"
        stroke-width="2"
      />
    {/if}
    {#each indices as i}
      <circle
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
</style>
