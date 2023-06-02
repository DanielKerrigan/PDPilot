<script lang="ts">
  import type { TwoWayPD } from '../../../types';
  import TwoWayHeatmap from './TwoWayHeatmap.svelte';
  import TwoWayLines from './TwoWayLines.svelte';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let showMarginalPdp: boolean;
  export let colorShows: 'predictions' | 'interactions';
  export let showColorLegend: boolean;
  export let colorLegendTitle = '';
  export let marginTop = 0;
  export let marginRight = 0;
  export let marginalPlotHeight: number;
  export let twoWayKind: 'heatmap' | 'lines' = 'heatmap';
</script>

{#if twoWayKind === 'heatmap'}
  <TwoWayHeatmap
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {showMarginalPdp}
    {colorShows}
    {showColorLegend}
    {marginTop}
    {marginRight}
    {marginalPlotHeight}
    {colorLegendTitle}
  />
{:else}
  <TwoWayLines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showColorLegend}
    {marginTop}
    {marginRight}
  />
{/if}

<style>
</style>
