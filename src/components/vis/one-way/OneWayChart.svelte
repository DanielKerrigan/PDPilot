<script lang="ts">
  import type {
    ICELevel,
    MarginalDistributionKind,
    OneWayPD,
  } from '../../../types';
  import ClusterBands from './ClusterBands.svelte';
  import ClusterLines from './ClusterLines.svelte';
  import ClusterCenters from './ClusterCenters.svelte';
  import Lines from './Lines.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let iceLevel: ICELevel;
  export let marginalDistributionKind: MarginalDistributionKind;
  export let marginTop: number;
  export let marginRight: number;
  export let indices: number[] | null;
</script>

{#if iceLevel === 'lines'}
  <Lines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {marginalDistributionKind}
    {marginTop}
    {marginRight}
  />
{:else if iceLevel === 'cluster-centers'}
  <ClusterCenters
    {pd}
    {width}
    {height}
    {scaleLocally}
    showMarginalDistribution={marginalDistributionKind === 'bars'}
  />
{:else if iceLevel === 'cluster-bands'}
  <ClusterBands
    {pd}
    {width}
    {height}
    {scaleLocally}
    showMarginalDistribution={marginalDistributionKind === 'bars'}
  />
{:else}
  <ClusterLines
    {pd}
    {width}
    {height}
    {scaleLocally}
    showMarginalDistribution={marginalDistributionKind === 'bars'}
    {indices}
  />
{/if}

<style>
</style>
