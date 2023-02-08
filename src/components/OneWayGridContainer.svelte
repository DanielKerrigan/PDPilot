<script lang="ts">
  import PDPGridControls from './PDPGridControls.svelte';
  import PDPGrid from './PDPGrid.svelte';
  import { feature_names, one_way_pds } from '../stores';
  import { singlePDPSortingOptions } from '../sorting';

  let selectedFeatures: string[] = $feature_names;

  $: filteredOneWayPds = $one_way_pds.filter((p) =>
    selectedFeatures.includes(p.x_feature)
  );
</script>

<div class="one-way-grid-container">
  <div>
    <PDPGridControls bind:selectedFeatures />
  </div>
  <div class="pdp-grid-wrapper">
    <PDPGrid
      data={filteredOneWayPds}
      sortingOptions={singlePDPSortingOptions}
    />
  </div>
</div>

<style>
  .one-way-grid-container {
    height: 100%;
    display: flex;
  }

  .pdp-grid-wrapper {
    flex: 1;
  }
</style>
