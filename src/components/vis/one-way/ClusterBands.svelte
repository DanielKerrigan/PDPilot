<script lang="ts">
  import type { OneWayPD } from '../../../types';
  import { scaleLinear, scaleOrdinal, scalePoint } from 'd3-scale';
  import { line as d3line, area as d3area } from 'd3-shape';
  import { zip } from 'd3-array';
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
  import { categoricalColors, getYScale } from '../../../vis-utils';
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

  $: y = getYScale(
    pd,
    chartHeight,
    facetHeight,
    'cluster-bands',
    scaleLocally,
    $ice_line_extent,
    $ice_cluster_center_extent,
    $ice_cluster_band_extent,
    $ice_cluster_line_extent,
    margin
  );

  $: clusterIds = pd.ice.clusters.map((d) => d.id);

  $: dark = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.dark);

  $: medium = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: light = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.light);

  $: line = d3line<number>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y((d) => y(d));

  $: area = d3area<number[]>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y1((d) => y(d[1]))
    .y0((d) => y(d[0]));
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

<div class="ice-cluster-container">
  {#each pd.ice.clusters as cluster}
    <div class="ice-cluster">
      <svg class="ice-cluster-chart" style:height={facetHeight} style:width>
        <path
          d={area(zip(cluster.p10, cluster.p90))}
          fill={light(cluster.id)}
        />

        <path
          d={area(zip(cluster.p25, cluster.p75))}
          fill={medium(cluster.id)}
        />

        <path
          d={line(cluster.centered_mean)}
          stroke={dark(cluster.id)}
          stroke-opacity="1"
          fill="none"
          stroke-width="2"
        />

        <path
          d={line(pd.ice.centered_pdp)}
          stroke="var(--black)"
          stroke-opacity="1"
          fill="none"
          stroke-width="2"
        />

        <YAxis scale={y} x={margin.left} label={'centered prediction'} />

        <XAxis
          scale={x}
          y={facetHeight - margin.bottom}
          showTickLabels={cluster.id === pd.ice.clusters.length - 1}
          showAxisLabel={cluster.id === pd.ice.clusters.length - 1}
          label={pd.x_feature}
          integerOnly={feature.subkind === 'discrete'}
          value_map={'value_map' in feature ? feature.value_map : {}}
        />
      </svg>
    </div>
  {/each}
</div>

<style>
  .ice-cluster-container {
    width: 100%;
    height: 100%;
  }

  .ice-cluster {
    display: flex;
  }
</style>
