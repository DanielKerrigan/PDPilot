<script lang="ts">
  import type { OneWayPD } from '../../../types';
  import { scaleLinear, scalePoint } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    ice_cluster_band_extent,
    ice_cluster_line_extent,
    feature_info,
  } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import { getYScale } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;

  $: feature = $feature_info[pd.x_feature];

  $: marginalChartHeight = showMarginalDistribution ? 100 : 0;

  const margin = { top: 10, right: 10, bottom: 35, left: 50 };

  $: chartHeight = height - marginalChartHeight;
  $: facetHeight = chartHeight / pd.ice.clusters.length;

  $: x =
    feature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_values[0], pd.x_values[pd.x_values.length - 1]])
          .range([margin.left, width - margin.right])
      : scalePoint<number>()
          .domain(pd.x_values)
          .range([margin.left, width - margin.right])
          .padding(0.5);

  $: radius = 'step' in x ? Math.min(3, x.step() / 2 - 1) : 0;

  $: y = getYScale(
    pd,
    chartHeight,
    facetHeight,
    'cluster-centers',
    scaleLocally,
    $ice_line_extent,
    $ice_cluster_center_extent,
    $ice_cluster_band_extent,
    $ice_cluster_line_extent,
    margin
  );

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: I = range(pd.x_values.length);

  $: line = d3line<number>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y((d) => y(d));
</script>

{#if showMarginalDistribution}
  <svg {width} height={marginalChartHeight}>
    {#if 'bandwidth' in x}
      <MarginalBarChart
        data={$feature_info[pd.x_feature].distribution}
        {x}
        height={marginalChartHeight}
        direction="horizontal"
      />
    {:else}
      <MarginalHistogram
        data={$feature_info[pd.x_feature].distribution}
        {x}
        height={marginalChartHeight}
        direction="horizontal"
      />
    {/if}
  </svg>
{/if}

<svg class="one-way-chart">
  <!-- cluster means -->
  <g>
    {#each pd.ice.clusters as cluster}
      <path
        d={line(cluster.centered_mean)}
        stroke={'var(--gray-2)'}
        stroke-width="2"
        fill="none"
      />

      {#if feature.kind === 'categorical'}
        <g>
          {#each I as i}
            <circle
              cx={x(pd.x_values[i])}
              cy={y(cluster.centered_mean[i])}
              r={radius}
              fill={'var(--gray-2)'}
            />
          {/each}
        </g>
      {/if}
    {/each}
  </g>

  <!-- PDP -->
  <path
    d={line(pd.ice.centered_pdp)}
    stroke="var(--black)"
    stroke-width="2"
    fill="none"
  />

  {#if feature.kind === 'categorical'}
    {#each I as i}
      <circle
        cx={x(pd.x_values[i])}
        cy={y(pd.ice.centered_pdp[i])}
        r={radius}
        fill="var(--black)"
      />
    {/each}
  {/if}

  <XAxis
    scale={x}
    y={chartHeight - margin.bottom}
    label={pd.x_feature}
    integerOnly={feature.subkind === 'discrete'}
    value_map={'value_map' in feature ? feature.value_map : {}}
  />

  <YAxis scale={y} x={margin.left} label={'centered avg. prediction'} />
</svg>

<style>
  .one-way-chart {
    width: 100%;
    height: 100%;
  }
</style>
