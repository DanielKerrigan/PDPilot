<script lang="ts">
  import TwoWayGridFilters from './TwoWayGridFilters.svelte';
  import PDPGrid from './PDPGrid.svelte';
  import { feature_names, two_way_pds } from '../stores';
  import { doublePDPSortingOptions } from '../sorting';

  let selectedFeatures: string[] = $feature_names;

  function onChangeFilters(event: CustomEvent<string[]>) {
    selectedFeatures = event.detail;
  }

  $: filteredTwoWayPds = $two_way_pds.filter(
    (p) =>
      selectedFeatures.includes(p.x_feature) &&
      selectedFeatures.includes(p.y_feature)
  );
</script>

<div class="two-way-grid-container">
  <div>
    <TwoWayGridFilters on:changeFilters={onChangeFilters} />
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
    min-width: 0;
  }
</style>
