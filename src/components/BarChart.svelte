<script lang="ts">
  import type { CategoricalSinglePDPData } from '../types';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import XAxis from './XAxis.svelte';
  import YAxis from './YAxis.svelte';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let predictionExtent: [number, number];

  const margin = { top: 5, right: 5, bottom: 40, left: 50 };

  $: x = scaleBand<string | number>()
    .domain(pdp.values.map((d) => d.x))
    .range([margin.left, width - margin.right])
    .paddingInner(0.1);

  $: y = scaleLinear()
    .domain(predictionExtent)
    .range([height - margin.bottom, margin.top]);
</script>

<svg {width} {height}>
  {#each pdp.values as d}
    <rect
      x={x(d.x)}
      y={y(d.avg_pred)}
      width={x.bandwidth()}
      height={y(predictionExtent[0]) - y(d.avg_pred)}
      fill="steelblue"
    />
  {/each}

  <XAxis scale={x} y={height - margin.bottom} label={pdp.x_feature} />

  <YAxis scale={y} x={margin.left} label={'average prediction'} />
</svg>

<style>
</style>
