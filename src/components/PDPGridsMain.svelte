<script lang="ts">
  import PDPGrid from './PDPGrid.svelte';
  import { single_pdps, double_pdps } from '../stores';
  import { doublePDPSortingOptions, singlePDPSortingOptions } from '../sorting';

  export let selectedFeatures: string[];

  $: filteredOneWayPds = $single_pdps.filter((p) =>
    selectedFeatures.includes(p.x_feature)
  );

  $: filteredTwoWayPds = $double_pdps.filter(
    (p) =>
      selectedFeatures.includes(p.x_feature) &&
      selectedFeatures.includes(p.y_feature)
  );
</script>

<div class="main-container">
  <PDPGrid
    title={'One-way'}
    data={filteredOneWayPds}
    showColorLegend={false}
    sortingOptions={singlePDPSortingOptions}
    on:zoom
  />

  {#if filteredTwoWayPds.length > 0}
    <PDPGrid
      title={'Two-way'}
      data={filteredTwoWayPds}
      showColorLegend={true}
      sortingOptions={doublePDPSortingOptions}
      on:zoom
    />
  {/if}
</div>

<style>
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>
