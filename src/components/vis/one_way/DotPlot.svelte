<script lang="ts">
  import type {
    CategoricalSinglePDPData,
    CategoricalMarginalDistribution,
    ICELevel,
  } from '../../../types';
  import { scalePoint, scaleBand, scaleOrdinal } from 'd3-scale';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    nice_pdp_extent,
    nice_ice_mean_extent,
    nice_ice_band_extent,
    nice_ice_line_extent,
  } from '../../../stores';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { getYScale } from '../../../vis-utils';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let iceLevel: ICELevel;
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

  $: fy = scaleBand<number>()
    .domain(pdp.ice.clusters.map((d) => d.id))
    .range([margin.top, height - margin.bottom])
    .paddingInner(0.2);

  $: y = getYScale(
    pdp,
    height,
    fy.bandwidth(),
    iceLevel,
    scaleLocally,
    $nice_pdp_extent,
    $nice_ice_mean_extent,
    $nice_ice_band_extent,
    $nice_ice_line_extent,
    margin
  );

  $: radius = Math.min(3, x.step() / 2 - 1);

  $: clusterIds = pdp.ice.clusters.map((d) => d.id);

  $: indices = range(pdp.x_values.length);

  $: dark = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(['#2171b5', '#238b45', '#cb181d', '#d94701', '#6a51a3']);

  $: medium = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(['#6baed6', '#74c476', '#fb6a4a', '#fd8d3c', '#9e9ac8']);

  $: light = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(['#bdd7e7', '#bae4b3', '#fcae91', '#fdbe85', '#cbc9e2']);

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: line = d3line<number>()
    .x((_, i) => x(pdp.x_values[i]) ?? 0)
    .y((d) => y(d));
</script>

<svg class="pdp-dot-plot">
  {#if iceLevel === 'none'}
    <!-- PDP -->
    <g>
      {#each indices as i}
        <circle
          cx={x(pdp.x_values[i])}
          cy={y(pdp.mean_predictions[i])}
          r={radius}
          fill="var(--black)"
        />
      {/each}
    </g>

    <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'average prediction'} />
  {:else if iceLevel === 'mean'}
    <!-- cluster means -->
    <g>
      {#each pdp.ice.clusters as cluster}
        <path
          d={line(cluster.centered_mean)}
          stroke={dark(cluster.id)}
          stroke-width="2"
          fill="none"
        />

        <g>
          {#each indices as i}
            <circle
              cx={x(pdp.x_values[i])}
              cy={y(cluster.centered_mean[i])}
              r={radius}
              fill={dark(cluster.id)}
            />
          {/each}
        </g>
      {/each}
    </g>

    <!-- PDP -->
    <path
      d={line(pdp.ice.centered_pdp)}
      stroke="var(--black)"
      stroke-width="2"
      fill="none"
    />

    {#each indices as i}
      <circle
        cx={x(pdp.x_values[i])}
        cy={y(pdp.ice.centered_pdp[i])}
        r={radius}
        fill="var(--black)"
      />
    {/each}

    <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

    <YAxis scale={y} x={margin.left} label={'centered average prediction'} />
  {:else if iceLevel === 'band'}
    <g>
      {#each pdp.ice.clusters as cluster}
        <g transform="translate(0,{fy(cluster.id)})">
          <!-- 10-90 percentile -->
          <g>
            {#each indices as i}
              <rect
                x={(x(pdp.x_values[i]) ?? 0) - radius}
                y={y(cluster.p90[i])}
                width={radius * 2}
                height={y(cluster.p10[i]) - y(cluster.p90[i])}
                fill={light(cluster.id)}
              />
            {/each}
          </g>

          <!-- 25-75 percentile -->
          <g>
            {#each indices as i}
              <rect
                x={(x(pdp.x_values[i]) ?? 0) - radius}
                y={y(cluster.p75[i])}
                width={radius * 2}
                height={y(cluster.p25[i]) - y(cluster.p75[i])}
                fill={medium(cluster.id)}
              />
            {/each}
          </g>

          <!-- cluster mean -->
          <g>
            {#each indices as i}
              <circle
                cx={x(pdp.x_values[i])}
                cy={y(cluster.centered_mean[i])}
                r={radius}
                fill={dark(cluster.id)}
              />
            {/each}
          </g>

          <!-- PDP -->
          <g>
            {#each indices as i}
              <circle
                cx={x(pdp.x_values[i])}
                cy={y(pdp.ice.centered_pdp[i])}
                r={radius}
                fill="var(--black)"
              />
            {/each}
          </g>

          <YAxis
            scale={y}
            x={margin.left}
            label={'centered average prediction'}
          />

          <XAxis
            scale={x}
            y={fy.bandwidth()}
            showTickLabels={cluster.id === pdp.ice.clusters.length - 1}
            showAxisLabel={cluster.id === pdp.ice.clusters.length - 1}
            label={pdp.x_feature}
          />
        </g>
      {/each}
    </g>
  {:else if iceLevel === 'line'}
    <g>
      {#each pdp.ice.clusters as cluster}
        <g transform="translate(0,{fy(cluster.id)})">
          <g>
            {#each cluster.centered_ice_lines as ice}
              <path
                d={line(ice)}
                stroke={light(cluster.id)}
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

          <g>
            {#each indices as i}
              <circle
                cx={x(pdp.x_values[i])}
                cy={y(cluster.mean[i])}
                r={radius}
                fill={dark(cluster.id)}
              />
            {/each}
          </g>

          <path
            d={line(pdp.ice.centered_pdp)}
            stroke="var(--black)"
            stroke-opacity="1"
            fill="none"
            stroke-width="2"
          />

          <g>
            {#each indices as i}
              <circle
                cx={x(pdp.x_values[i])}
                cy={y(pdp.ice.centered_pdp[i])}
                r={radius}
                fill="var(--black)"
              />
            {/each}
          </g>

          <YAxis
            scale={y}
            x={margin.left}
            label={'centered average prediction'}
          />
          <XAxis
            scale={x}
            y={fy.bandwidth()}
            showTickLabels={cluster.id === pdp.ice.clusters.length - 1}
            showAxisLabel={cluster.id === pdp.ice.clusters.length - 1}
            label={pdp.x_feature}
          />
        </g>
      {/each}
    </g>
  {/if}

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
