<script lang="ts">
  import PDPGrid from './PDPGrid.svelte';
  import { one_way_pds, two_way_pds } from '../stores';
  import { doublePDPSortingOptions, singlePDPSortingOptions } from '../sorting';

  export let selectedFeatures: string[];

  $: filteredOneWayPds = $one_way_pds.filter((p) =>
    selectedFeatures.includes(p.x_feature)
  );

  $: filteredTwoWayPds = $two_way_pds.filter(
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
    showShowIceClusters={true}
    sortingOptions={singlePDPSortingOptions}
    on:zoom
  />

  {#if filteredTwoWayPds.length > 0}
    <PDPGrid
      title={'Two-way'}
      data={filteredTwoWayPds}
      showColorLegend={true}
      showShowIceClusters={false}
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
