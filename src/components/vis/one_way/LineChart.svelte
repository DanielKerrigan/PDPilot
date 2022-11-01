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
  import {
    categoricalColors,
    defaultFormat,
    getYScale,
  } from '../../../vis-utils';

  export let pdp: QuantitativeSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let iceLevel: ICELevel;
  export let marginalDistributionX: QuantitativeMarginalDistribution | null;
  export let showClusterDescriptions: boolean;

  // this approach for generating a unique id to use for the
  // clip path comes from https://observablehq.com/@d3/difference-chart

  const clipPathId: string = Math.random().toString(16).slice(2);

  $: margin = {
    top: marginalDistributionX !== null ? 100 : 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: facetHeight =
    (height - margin.top - margin.bottom) / pdp.ice.clusters.length;

  $: x = scaleLinear()
    .domain([pdp.x_values[0], pdp.x_values[pdp.x_values.length - 1]])
    .range([
      margin.left,
      (showClusterDescriptions ? width / 2 : width) - margin.right,
    ]);

  $: y = getYScale(
    pdp,
    height,
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
</script>

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
            width={width - margin.left - margin.right}
            height={height - margin.top - margin.bottom}
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

    <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

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

    <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'centered average prediction'} />
  </svg>
{:else if iceLevel === 'band' || iceLevel === 'line'}
  <div class="ice-cluster-container">
    {#each pdp.ice.clusters as cluster}
      <div class="ice-cluster">
        <svg class="ice-cluster-chart">
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
              y={facetHeight}
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
        {#if showClusterDescriptions}
          <div class="ice-cluster-description">
            <div class="ice-cluster-description-header">Rule</div>
            <div class="ice-cluster-description-header ice-cluster-justify-end">
              Accuracy
            </div>
            {#each cluster.rules as rule}
              <div class="ice-cluster-rule">
                {#each rule.conditions as condition, i}
                  <div class="ice-cluster-condition">
                    {condition.feature}
                    {#if condition.sign === 'lte'}
                      ≤
                    {:else if condition.sign === 'gt'}
                      >
                    {/if}
                    {defaultFormat(condition.threshold)}
                  </div>
                  {#if i < rule.conditions.length - 1}
                    <div>and</div>
                  {/if}
                {/each}
              </div>
              <div class="ice-cluster-rule-stats ice-cluster-justify-end">
                {rule.num_correct}/{rule.num_instances}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>
{/if}

{#if marginalDistributionX !== null}
  <MarginalHistogram
    data={marginalDistributionX}
    {x}
    height={margin.top}
    direction="horizontal"
  />
{/if}

<style>
  .pdp-line-chart {
    width: 100%;
    height: 100%;
  }

  .ice-cluster-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .ice-cluster {
    display: flex;
    height: 100%;
  }

  .ice-cluster-chart {
    flex: 1;
  }

  .ice-cluster-description {
    flex: 1;

    display: grid;
    grid-template-columns: 1fr min-content;
    grid-auto-rows: max-content;
    column-gap: 0.25em;
  }

  .ice-cluster-rule {
    display: flex;
    gap: 0.5em;
    overflow-x: auto;
  }

  .ice-cluster-description-header {
    font-weight: bold;
  }

  .ice-cluster-condition {
    white-space: nowrap;
  }

  .ice-cluster-justify-end {
    justify-self: end;
  }
</style>
