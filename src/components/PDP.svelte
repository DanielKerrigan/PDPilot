<script lang="ts">
  import type { OneWayPD, TwoWayPD, ICELevel } from '../types';
  import OneWayPDP from './vis/one-way/OneWayPDP.svelte';
  import TwoWayPDP from './vis/two-way/TwoWayPDP.svelte';

  export let pd: OneWayPD | TwoWayPD;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let showMarginalDistribution: boolean;
  export let showInteractions: boolean = false;
  export let showColorLegend: boolean = false;
  export let iceLevel: ICELevel;
</script>

{#if width > 0 && height > 0}
  {#if pd.num_features === 1}
    <OneWayPDP
      {width}
      {height}
      {pd}
      {scaleLocally}
      {showTrendLine}
      {iceLevel}
      {showMarginalDistribution}
    />
  {:else if pd.num_features === 2}
    <TwoWayPDP
      {width}
      {height}
      {pd}
      {globalColor}
      {scaleLocally}
      {showInteractions}
      {showColorLegend}
      {showMarginalDistribution}
    />
  {/if}
{/if}

<style>
</style>
