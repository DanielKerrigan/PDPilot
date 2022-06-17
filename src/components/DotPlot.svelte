<script lang="ts">
  import type {CategoricalSinglePDPData} from '../types';
  import * as d3 from 'd3';
  import XAxis from './XAxis.svelte';
  import YAxis from './YAxis.svelte';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let predictionExtent: [number, number];

  const margin = { top: 10, right: 10, bottom: 40, left: 50 };

  $: x = d3.scalePoint<string | number>()
    .domain(pdp.values.map(d => d.x))
    .range([margin.left, width - margin.right])
    .padding(0.5);

  $: y = d3.scaleLinear()
    .domain(predictionExtent)
    .range([height - margin.bottom, margin.top]);

  $: radius = Math.min(3, x.step() / 2 - 1);
</script>

<svg class="pdp-dot-plot">
  {#each pdp.values as d}
    <circle
      cx={x(d.x)}
      cy={y(d.avg_pred)}
      r={radius}
      fill="steelblue"
    />
  {/each}

  <XAxis
    scale={x}
    y={height - margin.bottom}
    label={pdp.x_feature}
  />

  <YAxis
    scale={y}
    x={margin.left}
    label={'average prediction'}
  />
</svg>

<style>
  .pdp-dot-plot {
    width: 100%;
    height: 100%;
  }
</style>