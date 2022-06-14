<script lang="ts">
  import type {PDPData} from '../types';
  import LineChart from './LineChart.svelte';
  import DotPlot from './DotPlot.svelte';
  import QuantitativeHeatmap from './QuantitativeHeatmap.svelte';

  export let pdp: PDPData;
  export let predictionExtent: [number, number];
  export let color: d3.ScaleSequential<string, string>;

  let width: number;
  let height: number;
</script>

<div bind:clientWidth={width} bind:clientHeight={height}>
  {#if width != null && height != null}
    {#if pdp.type === 'quantitative-single'}
      <LineChart {width} {height} {pdp} {predictionExtent}/>
    {:else if pdp.type === 'categorical-single'}
      <DotPlot {width} {height} {pdp} {predictionExtent}/>
    {:else if pdp.type === 'quantitative-double'}
      <QuantitativeHeatmap {width} {height} {pdp} {color}/>
    {/if}
  {/if}
</div>

<style>
  div {
    width: 100%;
    height: 100%;
  }
</style>