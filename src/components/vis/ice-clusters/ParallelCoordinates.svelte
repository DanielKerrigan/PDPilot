<script lang="ts">
  import { scaleBand } from 'd3-scale';
  import { range } from 'd3-array';
  import { dataset } from '../../../stores';
  import type { OneWayPD } from '../../../types';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let features: string[];

  $: clusterIds = range(pd.ice.clusters.length);

  $: fy = scaleBand<number>().domain(clusterIds).range([0, height]);
</script>

<svg {width} {height}>
  {#each clusterIds as id}
    <g />
  {/each}
</svg>

<style>
</style>
