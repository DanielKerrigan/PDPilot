<script lang="ts">
  import TwoWayGridFilters from './TwoWayGridFilters.svelte';
  import PDPGrid from './PDPGrid.svelte';
  import { feature_names, two_way_pds } from '../stores';
  import { doublePDPSortingOptions } from '../sorting';

  let selectedFeatures: string[] = $feature_names;
  let op: 'and' | 'or' = 'and';

  function onChangeFilters(
    event: CustomEvent<{ features: string[]; op: 'and' | 'or' }>
  ) {
    selectedFeatures = event.detail.features;
    op = event.detail.op;
  }

  $: filteredTwoWayPds = $two_way_pds.filter((p) =>
    op === 'and'
      ? selectedFeatures.includes(p.x_feature) &&
        selectedFeatures.includes(p.y_feature)
      : selectedFeatures.includes(p.x_feature) ||
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
      noPlotsMessage={selectedFeatures.length === 1 && op === 'and'
        ? 'No plots to show.'
        : 'No plots to show. PDPilot only pre-computes two-way PDPs when it detects likely interaction between the pair of features.'}
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
