<script lang="ts">
  import type {
    QuantitativeMarginalDistribution,
    QuantitativeSinglePDPData,
  } from '../../../types';
  import { scaleLinear, scaleOrdinal } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_pdp_extent, nice_cluster_extent } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import { schemeTableau10 } from 'd3-scale-chromatic';

  export let pdp: QuantitativeSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let numIceInstances: number;
  export let showIceClusters: boolean;
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
    .domain(showIceClusters ? $nice_cluster_extent : $nice_pdp_extent)
    .range([height - margin.bottom, margin.top]);

  $: yLocal = scaleLinear()
    .domain(
      numIceInstances > 0
        ? [pdp.ice.ice_min, pdp.ice.ice_max]
        : showIceClusters
        ? [pdp.ice.mean_min, pdp.ice.mean_max]
        : [pdp.pdp_min, pdp.pdp_max]
    )
    .nice()
    .range([height - margin.bottom, margin.top]);

  $: y = scaleLocally ? yLocal : yGlobal;

  $: color = scaleOrdinal<number, string>()
    .domain(pdp.ice.clusters.map((d) => d.id))
    .range(schemeTableau10);

  function iceColor(id: number, numIceInstances: number): string {
    if (numIceInstances > 0) {
      return color(id);
    } else {
      return 'var(--gray-3)';
    }
  }

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: indices = range(pdp.x_values.length);

  $: pdpLine = d3line<number>()
    .x((i) => x(pdp.x_values[i]))
    .y((i) => y(pdp.mean_predictions[i]));

  $: trendLine = d3line<number>()
    .x((i) => x(pdp.x_values[i]))
    .y((i) => y(pdp.trend_good_fit[i]));

  $: iceLine = d3line<number>()
    .x((_, i) => x(pdp.x_values[i]))
    .y((d) => y(d));
</script>

<!--
  setting the width and height in pixels, as with

  <svg width={width} height={height}>

  or

  <svg style="width: {width}; height: {height};">

  was causing issues with resizing.
-->
<svg class="pdp-line-chart">
  <!-- trend line -->
  {#if showTrendLine}
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

    <path
      class="line"
      d={trendLine(indices)}
      stroke="var(--gray-5)"
      fill="none"
      stroke-width="2"
      clip-path="url(#{clipPathId})"
    />
  {/if}

  <!-- ICE clusters -->
  {#if showIceClusters}
    <g>
      {#each pdp.ice.clusters as cluster}
        {#if numIceInstances > 0}
          {#each cluster.ice_lines.slice(0, numIceInstances) as ice}
            <path
              class="line"
              d={iceLine(ice)}
              stroke={iceColor(cluster.id, numIceInstances)}
              stroke-opacity="0.4"
              fill="none"
              stroke-width="1"
            />
          {/each}
        {/if}

        <path
          class="line"
          d={iceLine(cluster.mean)}
          stroke={iceColor(cluster.id, numIceInstances)}
          stroke-opacity="1"
          fill="none"
          stroke-width="2"
        />
      {/each}
    </g>
  {/if}

  <!-- PDP -->
  <path
    class="line"
    d={pdpLine(indices)}
    stroke="var(--black)"
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
</style>
