<script lang="ts">
  import type { OneWayPD, TwoWayPD, ICELevel } from '../types';
  import OneWayChart from './vis/one-way/OneWayChart.svelte';
  import TwoWayChart from './vis/two-way/TwoWayChart.svelte';

  export let pd: OneWayPD | TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let colorShows: 'predictions' | 'interactions' = 'predictions';
  export let showColorLegend = false;
  export let colorLegendTitle = '';
  export let iceLevel: ICELevel;
  export let indices: number[] | null = null;
  export let showMarginalDistribution = false;
  export let showMarginalPdp = false;
  export let marginTop = 0;
  export let marginRight = 0;
  export let marginalPlotHeight = 0;
  export let allowBrushing = false;
  export let showBrushedBorder = false;
  export let iceLineWidth = 1;
  export let twoWayKind: 'lines' | 'heatmap' = 'heatmap';
</script>

{#if width > 0 && height > 0}
  {#if pd.num_features === 1}
    <OneWayChart
      {width}
      {height}
      {pd}
      {scaleLocally}
      {iceLevel}
      {showMarginalDistribution}
      {marginTop}
      {marginalPlotHeight}
      {indices}
      {allowBrushing}
      {showBrushedBorder}
      {iceLineWidth}
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
      {marginalPlotHeight}
      {showMarginalDistribution}
      {showMarginalPdp}
      {twoWayKind}
      {colorLegendTitle}
    />
  {/if}
{/if}

<style>
</style>
