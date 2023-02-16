<script lang="ts">
  import type { ICELevel, OneWayPD } from '../../../types';
  import ClusterBands from './ClusterBands.svelte';
  import ClusterLines from './ClusterLines.svelte';
  import ClusterCenters from './ClusterCenters.svelte';
  import Lines from './Lines.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let iceLevel: ICELevel;
  export let showMarginalDistribution: boolean;
  export let marginTop: number;
  export let marginRight: number;
  export let indices: number[] | null;
  export let allowBrushing: boolean;
</script>

{#if iceLevel === 'lines'}
  <Lines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {marginTop}
    {marginRight}
    {allowBrushing}
  />
{:else if iceLevel === 'cluster-centers'}
  <ClusterCenters
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {marginTop}
    {marginRight}
  />
{:else if iceLevel === 'cluster-bands'}
  <ClusterBands
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {marginTop}
    {marginRight}
  />
{:else}
  <ClusterLines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {marginTop}
    {marginRight}
    {indices}
  />
{/if}

<style>
</style>
