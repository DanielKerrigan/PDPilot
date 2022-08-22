<script lang="ts">
  import PDPGroup from './PDPGroup.svelte';
  import { filteredOneWayPds, filteredTwoWayPds } from '../stores';
  import { doublePDPSortingOptions, singlePDPSortingOptions } from '../sorting';
</script>

<div class="main-container">
  <PDPGroup
    title={'One-way'}
    data={$filteredOneWayPds}
    showColorLegend={false}
    sortingOptions={singlePDPSortingOptions}
  />

  {#if $filteredTwoWayPds.length > 0}
    <PDPGroup
      title={'Two-way'}
      data={$filteredTwoWayPds}
      showColorLegend={true}
      sortingOptions={doublePDPSortingOptions}
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
