<script lang="ts">
  import type {
    CategoricalSinglePDPData,
    OneWayQuantitativeCluster,
    OneWayCategoricalCluster,
    QuantitativeSinglePDPData,
  } from '../types';
  import { isQuantitativeOneWayPdArray } from '../types';
  import MultiLineChart from './vis/clusters/MultiLineChart.svelte';

  export let cluster: OneWayQuantitativeCluster | OneWayCategoricalCluster;
  export let pds: QuantitativeSinglePDPData[] | CategoricalSinglePDPData[];
  export let width: number;
  export let height: number;
</script>

{#if cluster.kind === 'quantitative' && isQuantitativeOneWayPdArray(pds)}
  <MultiLineChart {cluster} {pds} {width} {height} />
{:else if cluster.kind === 'categorical' && !isQuantitativeOneWayPdArray(pds)}
  <div class="categorical-cluster">
    <div>Categorical cluster</div>
  </div>
{/if}

<style>
  .categorical-cluster {
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
