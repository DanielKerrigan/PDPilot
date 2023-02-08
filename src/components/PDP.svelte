<script lang="ts">
  import type {
    OneWayPD,
    TwoWayPD,
    ICELevel,
    MarginalDistributionKind,
  } from '../types';
  import OneWayChart from './vis/one-way/OneWayChart.svelte';
  import TwoWayChart from './vis/two-way/TwoWayChart.svelte';

  export let pd: OneWayPD | TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let colorShows: 'predictions' | 'interactions' = 'predictions';
  export let showColorLegend = false;
  export let iceLevel: ICELevel;
  export let indices: number[] | null = null;
  export let marginalDistributionKind: MarginalDistributionKind = 'none';
  export let marginTop = 0;
  export let marginRight = 0;
</script>

{#if width > 0 && height > 0}
  {#if pd.num_features === 1}
    <OneWayChart
      {width}
      {height}
      {pd}
      {scaleLocally}
      {iceLevel}
      {marginalDistributionKind}
      {marginTop}
      {marginRight}
      {indices}
    />
  {:else if pd.num_features === 2}
    <TwoWayChart
      {width}
      {height}
      {pd}
      {scaleLocally}
      {colorShows}
      {showColorLegend}
      {marginTop}
      {marginRight}
      showMarginalDistribution={marginalDistributionKind === 'bars'}
    />
  {/if}
{/if}

<style>
</style>
