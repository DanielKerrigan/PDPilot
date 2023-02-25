<script lang="ts">
  import type { ICELevel, OneWayPD } from '../../../types';
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
  export let distributionHeight: number;
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
    {distributionHeight}
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
    {distributionHeight}
  />
{:else}
  <ClusterLines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {marginTop}
    {distributionHeight}
    {indices}
  />
{/if}

<style>
</style>
