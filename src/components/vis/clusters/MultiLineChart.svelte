<script lang="ts">
  import type {
    OneWayQuantitativeCluster,
    QuantitativeSinglePDPData,
  } from '../../../types';
  import { scaleLinear } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_prediction_extent } from '../../../stores';

  export let cluster: OneWayQuantitativeCluster;
  export let pds: QuantitativeSinglePDPData[];
  export let width: number;
  export let height: number;

  $: maxLength = Math.max(...pds.map((d) => d.mean_predictions.length));
  $: indices = range(maxLength);

  $: margin = {
    top: 20,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: x = scaleLinear()
    .domain([indices[0], indices[indices.length - 1]])
    .range([margin.left, width - margin.right]);

  $: y = scaleLinear()
    .domain($nice_prediction_extent)
    .range([height - margin.bottom, margin.top]);

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: pdpLine = d3line<number>()
    .x((d, i) => x(i))
    .y((d, i) => y(d));
</script>

<svg class="multi-line-chart">
  <text
    dominant-baseline="hanging"
    x={margin.left}
    y={2}
    font-size={12}
    font-weight="bold"
  >
    Cluster {cluster.id + 1}
  </text>

  {#each pds as pd}
    <path
      class="line"
      d={pdpLine(pd.mean_predictions)}
      stroke="var(--magenta)"
      stroke-width="1"
      stroke-opacity="0.5"
      fill="none"
    />
  {/each}

  <YAxis scale={y} x={margin.left} label={'average prediction'} />
</svg>

<style>
  .multi-line-chart {
    width: 100%;
    height: 100%;
  }
</style>
