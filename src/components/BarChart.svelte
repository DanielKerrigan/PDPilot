<script lang="ts">
  import type {CategoricalSinglePDPData} from '../types';
  import * as d3 from 'd3';
  import XAxis from './XAxis.svelte';
  import YAxis from './YAxis.svelte';

  export let pdp: CategoricalSinglePDPData;
  export let width: number;
  export let height: number;
  export let predictionExtent: [number, number];

  const margin = { top: 5, right: 5, bottom: 40, left: 50 };

  $: x = d3.scaleBand<string | number>()
    .domain(pdp.values.map(d => d.x))
    .range([margin.left, width - margin.right])
    .paddingInner(0.1);

  $: y = d3.scaleLinear()
    .domain(predictionExtent)
    .range([height - margin.bottom, margin.top]);
</script>

<svg width={width} height={height}>
  {#each pdp.values as d}
    <rect
      x={x(d.x)}
      y={y(d.avg_pred)}
      width={x.bandwidth()}
      height={y(predictionExtent[0]) - y(d.avg_pred)}
      fill="steelblue"
    />
  {/each}

  <XAxis
    scale={x}
    width={width}
    height={height}
    margin={margin}
    label={pdp.x_feature}
    x={0}
    y={height - margin.bottom}
  />

  <YAxis
    scale={y}
    width={width}
    height={height}
    margin={margin}
    x={margin.left}
    y={0}
    label={'average prediction'}
  />
</svg>

<style>
</style>