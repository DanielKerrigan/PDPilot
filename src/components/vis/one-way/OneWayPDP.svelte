<script lang="ts">
  import type { ICELevel, OneWayPD } from '../../../types';
  import { scaleLinear, scaleOrdinal, scalePoint } from 'd3-scale';
  import { line as d3line, area as d3area } from 'd3-shape';
  import { zip, range } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    nice_pdp_extent,
    nice_ice_mean_extent,
    nice_ice_band_extent,
    nice_ice_line_extent,
    feature_info,
  } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import { categoricalColors, getYScale } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let iceLevel: ICELevel;
  export let showMarginalDistribution: boolean;

  $: feature = $feature_info[pd.x_feature];

  // this approach for generating a unique id to use for the
  // clip path comes from https://observablehq.com/@d3/difference-chart

  const clipPathId: string = Math.random().toString(16).slice(2);

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
    iceLevel,
    scaleLocally,
    $nice_pdp_extent,
    $nice_ice_mean_extent,
    $nice_ice_band_extent,
    $nice_ice_line_extent,
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

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: I = range(pd.x_values.length);

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

{#if iceLevel === 'none'}
  <!--
    setting the width and height in pixels, as with

    <svg width={width} height={height}>

    or

    <svg style="width: {width}; height: {height};">

    was causing issues with resizing.
  -->
  <svg class="pdp-line-chart">
    <!-- trend line -->
    {#if showTrendLine && pd.ordered}
      <g>
        <clipPath id={clipPathId}>
          <rect
            x={margin.left}
            y={margin.top}
            width={width - margin.left - margin.right}
            height={chartHeight - margin.top - margin.bottom}
            fill="white"
          />
        </clipPath>
      </g>

      <path
        d={line(pd.trend_good_fit)}
        stroke="var(--gray-5)"
        fill="none"
        stroke-width="2"
        clip-path="url(#{clipPathId})"
      />
    {/if}

    <!-- PDP -->
    {#if pd.ordered}
      <path
        d={line(pd.mean_predictions)}
        stroke="var(--black)"
        stroke-width="2"
        fill="none"
      />
    {/if}

    {#if feature.kind === 'categorical'}
      <g>
        {#each I as i}
          <circle
            cx={x(pd.x_values[i])}
            cy={y(pd.mean_predictions[i])}
            r={radius}
            fill="var(--black)"
          />
        {/each}
      </g>
    {/if}

    <XAxis
      scale={x}
      y={chartHeight - margin.bottom}
      label={pd.x_feature}
      integerOnly={feature.subkind === 'discrete'}
      value_map={'value_map' in feature ? feature.value_map : {}}
    />

    <YAxis scale={y} x={margin.left} label={'average prediction'} />
  </svg>
{:else if iceLevel === 'mean'}
  <svg class="pdp-line-chart">
    <!-- cluster means -->
    <g>
      {#each pd.ice.clusters as cluster}
        <path
          d={line(cluster.centered_mean)}
          stroke={dark(cluster.id)}
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
                fill={dark(cluster.id)}
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

    <YAxis scale={y} x={margin.left} label={'centered average prediction'} />
  </svg>
{:else if iceLevel === 'band' || iceLevel === 'line'}
  <div class="ice-cluster-container">
    {#each pd.ice.clusters as cluster}
      <div class="ice-cluster">
        <svg class="ice-cluster-chart" style:height={facetHeight} style:width>
          {#if iceLevel === 'band'}
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

            <YAxis
              scale={y}
              x={margin.left}
              label={'centered average prediction'}
            />

            <XAxis
              scale={x}
              y={facetHeight - margin.bottom}
              showTickLabels={cluster.id === pd.ice.clusters.length - 1}
              showAxisLabel={cluster.id === pd.ice.clusters.length - 1}
              label={pd.x_feature}
              integerOnly={feature.subkind === 'discrete'}
              value_map={'value_map' in feature ? feature.value_map : {}}
            />
          {:else if iceLevel === 'line'}
            <g>
              <g>
                {#each cluster.centered_ice_lines as ice}
                  <path
                    d={line(ice)}
                    stroke={medium(cluster.id)}
                    stroke-opacity="0.5"
                    fill="none"
                    stroke-width="1"
                  />
                {/each}
              </g>

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

              <YAxis
                scale={y}
                x={margin.left}
                label={'centered average prediction'}
              />
              <XAxis
                scale={x}
                y={facetHeight - margin.bottom}
                showTickLabels={cluster.id === pd.ice.clusters.length - 1}
                showAxisLabel={cluster.id === pd.ice.clusters.length - 1}
                label={pd.x_feature}
                integerOnly={feature.subkind === 'discrete'}
                value_map={'value_map' in feature ? feature.value_map : {}}
              />
            </g>
          {/if}
        </svg>
      </div>
    {/each}
  </div>
{/if}

<style>
  .pdp-line-chart {
    width: 100%;
    height: 100%;
  }

  .ice-cluster-container {
    width: 100%;
    height: 100%;
  }

  .ice-cluster {
    display: flex;
  }
</style>
