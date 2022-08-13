<script lang="ts">
  import PDP from './PDP.svelte';
  import type { SinglePDPData, DoublePDPData } from '../types';
  import ZoomedPDP from './ZoomedPDP.svelte';

  export let pdp: SinglePDPData | DoublePDPData;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean = true;

  let showZoomedChart: boolean = false;

  function onClick() {
    showZoomedChart = true;
  }

  function hideZoomedChart() {
    showZoomedChart = false;
  }

  function onkeydown(ev: KeyboardEvent) {
    if (ev.key === 'Enter' || ev.key === ' ') {
      showZoomedChart = true;
    }
  }
</script>

{#if showZoomedChart}
  <ZoomedPDP
    {pdp}
    {globalColor}
    {scaleLocally}
    {showTrendLine}
    on:close={hideZoomedChart}
  />
{/if}

<div on:click={onClick} tabindex="0" on:keydown={onkeydown}>
  <PDP
    {pdp}
    {globalColor}
    {width}
    {height}
    {scaleLocally}
    showTrendLine={true}
    showMarginalDistribution={false}
    showColorLegend={scaleLocally}
  />
</div>

<style>
  div {
    cursor: pointer;
  }
</style>
