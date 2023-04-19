<script lang="ts">
  import type { TwoWayPD } from '../../../types';
  import TwoWayHeatmap from './TwoWayHeatmap.svelte';
  import TwoWayLines from './TwoWayLines.svelte';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let colorShows: 'predictions' | 'interactions';
  export let showColorLegend: boolean;
  export let colorLegendTitle = '';
  export let marginTop = 0;
  export let marginRight = 0;
  export let distributionHeight: number;
  export let twoWayKind: 'heatmap' | 'lines' = 'heatmap';
</script>

{#if twoWayKind === 'heatmap'}
  <TwoWayHeatmap
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {colorShows}
    {showColorLegend}
    {marginTop}
    {marginRight}
    {distributionHeight}
    {colorLegendTitle}
  />
{:else}
  <TwoWayLines
    {pd}
    {width}
    {height}
    {scaleLocally}
    {showMarginalDistribution}
    {colorShows}
    {showColorLegend}
    {marginTop}
    {marginRight}
    {distributionHeight}
  />
{/if}

<style>
</style>
