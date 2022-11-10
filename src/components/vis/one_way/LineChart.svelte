<script lang="ts">
  import type {
    ICELevel,
    QuantitativeMarginalDistribution,
    QuantitativeSinglePDPData,
  } from '../../../types';
  import { scaleLinear, scaleOrdinal } from 'd3-scale';
  import { line as d3line, area as d3area } from 'd3-shape';
  import { zip } from 'd3-array';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    nice_pdp_extent,
    nice_ice_mean_extent,
    nice_ice_band_extent,
    nice_ice_line_extent,
  } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import { categoricalColors, getYScale } from '../../../vis-utils';
  import RuleTree from '../rule/RuleTree.svelte';
  import RuleTable from '../rule/RuleTable.svelte';

  export let pdp: QuantitativeSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let iceLevel: ICELevel;
  export let marginalDistributionX: QuantitativeMarginalDistribution | null;
  export let clusterDescriptions: 'none' | 'tree' | 'table';
  export let iceLines: number[] = [];

  $: console.log(iceLines);

  // this approach for generating a unique id to use for the
  // clip path comes from https://observablehq.com/@d3/difference-chart

  const clipPathId: string = Math.random().toString(16).slice(2);

  $: marginalChartHeight = marginalDistributionX !== null ? 100 : 0;

  const margin = { top: 10, right: 10, bottom: 35, left: 50 };

  $: chartHeight = height - marginalChartHeight;
  $: facetHeight = chartHeight / pdp.ice.clusters.length;

  $: chartAndFacetWidth = clusterDescriptions !== 'none' ? width / 2 : width;

  $: x = scaleLinear()
    .domain([pdp.x_values[0], pdp.x_values[pdp.x_values.length - 1]])
    .range([margin.left, chartAndFacetWidth - margin.right]);

  $: y = getYScale(
    pdp,
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

  $: clusterIds = pdp.ice.clusters.map((d) => d.id);

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

  $: line = d3line<number>()
    .x((_, i) => x(pdp.x_values[i]))
    .y((d) => y(d));

  $: area = d3area<number[]>()
    .x((_, i) => x(pdp.x_values[i]))
    .y1((d) => y(d[1]))
    .y0((d) => y(d[0]));

  $: interactingFeatures = [
    ...new Set(
      pdp.ice.clusters
        .map((c) => c.rule_list.map((r: any) => Object.keys(r.conditions)))
        .flat(2)
    ),
  ];
</script>

{#if marginalDistributionX !== null}
  <svg width={chartAndFacetWidth} height={marginalChartHeight}>
    <MarginalHistogram
      data={marginalDistributionX}
      {x}
      height={marginalChartHeight}
      direction="horizontal"
    />
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
    {#if showTrendLine}
      <g>
        <clipPath id={clipPathId}>
          <rect
            x={margin.left}
            y={margin.top}
            width={chartAndFacetWidth - margin.left - margin.right}
            height={chartHeight - margin.top - margin.bottom}
            fill="white"
          />
        </clipPath>
      </g>

      <path
        d={line(pdp.trend_good_fit)}
        stroke="var(--gray-5)"
        fill="none"
        stroke-width="2"
        clip-path="url(#{clipPathId})"
      />
    {/if}

    <!-- PDP -->
    <path
      d={line(pdp.mean_predictions)}
      stroke="var(--black)"
      stroke-width="2"
      fill="none"
    />

    <XAxis scale={x} y={chartHeight - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'average prediction'} />
  </svg>
{:else if iceLevel === 'mean'}
  <svg class="pdp-line-chart">
    <!-- cluster means -->
    <g>
      {#each pdp.ice.clusters as cluster}
        <path
          d={line(cluster.centered_mean)}
          stroke={dark(cluster.id)}
          stroke-width="2"
          fill="none"
        />
      {/each}
    </g>

    <!-- PDP -->
    <path
      d={line(pdp.ice.centered_pdp)}
      stroke="var(--black)"
      stroke-width="2"
      fill="none"
    />

    <XAxis scale={x} y={chartHeight - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'centered average prediction'} />
  </svg>
{:else if iceLevel === 'filt'}
  <svg class="pdp-line-chart">
    <!-- ice lines -->
    <g>
      {#each iceLines as i}
        <path
          d={line(pdp.ice.centered_ice_lines[i])}
          stroke={'black'}
          stroke-width="2"
          stroke-opacity={0.5}
          fill="none"
        />
      {/each}
    </g>

    <XAxis scale={x} y={chartHeight - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'centered average prediction'} />
  </svg>
{:else if iceLevel === 'band' || iceLevel === 'line'}
  <div class="ice-cluster-container">
    {#each pdp.ice.clusters as cluster}
      <div class="ice-cluster">
        <svg
          class="ice-cluster-chart"
          style:height={facetHeight}
          style:width={chartAndFacetWidth}
        >
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
              d={line(pdp.ice.centered_pdp)}
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
              showTickLabels={cluster.id === pdp.ice.clusters.length - 1}
              showAxisLabel={cluster.id === pdp.ice.clusters.length - 1}
              label={pdp.x_feature}
            />
          {:else if iceLevel === 'line'}
            <g>
              <g>
                {#each cluster.centered_ice_lines as ice}
                  <path
                    d={line(ice)}
                    stroke={medium(cluster.id)}
                    stroke-opacity="1"
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
                d={line(pdp.ice.centered_pdp)}
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
                y={facetHeight}
                showTickLabels={cluster.id === pdp.ice.clusters.length - 1}
                showAxisLabel={cluster.id === pdp.ice.clusters.length - 1}
                label={pdp.x_feature}
              />
            </g>
          {/if}
        </svg>
        {#if clusterDescriptions !== 'none'}
          <div
            class="ice-cluster-description-container"
            style:max-height="{facetHeight}px"
            style:max-width="{chartAndFacetWidth}px"
            style:padding="{margin.top}px 0 {margin.bottom}px 0"
          >
            <div class="ice-cluster-description-content">
              {#if clusterDescriptions === 'tree'}
                <RuleTree node={cluster.rule_tree} pd={pdp} />
              {:else if clusterDescriptions === 'table'}
                <RuleTable
                  rules={cluster.rule_list}
                  features={interactingFeatures}
                  showFeatureNames={true}
                />
              {/if}
            </div>
          </div>
        {/if}
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

  .ice-cluster-description-content {
    overflow: auto;
    width: 100%;
    height: 100%;
  }
</style>
