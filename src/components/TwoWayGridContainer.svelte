<script lang="ts">
  import PDPGridControls from './PDPGridControls.svelte';
  import PDPGrid from './PDPGrid.svelte';
  import { feature_names, two_way_pds } from '../stores';
  import { doublePDPSortingOptions } from '../sorting';

  let selectedFeatures: string[] = $feature_names;

  $: filteredTwoWayPds = $two_way_pds.filter(
    (p) =>
      selectedFeatures.includes(p.x_feature) &&
      selectedFeatures.includes(p.y_feature)
  );
</script>

<div class="two-way-grid-container">
  <div>
    <PDPGridControls bind:selectedFeatures />
  </div>
  <div class="pdp-grid-wrapper">
    <PDPGrid
      data={filteredTwoWayPds}
      sortingOptions={doublePDPSortingOptions}
    />
  </div>
</div>

<style>
  .two-way-grid-container {
    height: 100%;
    display: flex;
  }

  .pdp-grid-wrapper {
    flex: 1;
  }
</style>
