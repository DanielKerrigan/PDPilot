<script lang="ts">
  import OneWayGridFilters from './OneWayGridFilters.svelte';
  import PDPGrid from './PDPGrid.svelte';
  import { feature_names, one_way_pds } from '../stores';
  import { singlePDPSortingOptions } from '../sorting';

  let selectedFeatures: string[] = $feature_names;

  function onChangeFilters(event: CustomEvent<string[]>) {
    selectedFeatures = event.detail;
  }

  $: filteredOneWayPds = $one_way_pds.filter((p) =>
    selectedFeatures.includes(p.x_feature)
  );
</script>

<div class="one-way-grid-container">
  <div>
    <OneWayGridFilters on:changeFilters={onChangeFilters} />
  </div>
  <div class="pdp-grid-wrapper">
    <PDPGrid
      data={filteredOneWayPds}
      sortingOptions={singlePDPSortingOptions}
      noPlotsMessage={'No plots to show.'}
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
    min-width: 0;
  }
</style>
