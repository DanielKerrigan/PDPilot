<script lang="ts">
  import FeatureNameFilter from './FeatureNameFilter.svelte';
  import FeatureKindFilter from './FeatureKindFilter.svelte';
  import ToggleHeader from './ToggleHeader.svelte';
  import { feature_names, feature_info, featureToPd } from '../stores';
  import type { ShapeSelections } from '../types';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ changeFilters: string[] }>();

  let showFeatureType = false;
  let showFeatureName = false;

  let shapeSelections: ShapeSelections;

  function onChangeKindFilters(event: CustomEvent<ShapeSelections>) {
    shapeSelections = event.detail;
  }

  function onChangeNameFilters(event: CustomEvent<string[]>) {
    dispatch('changeFilters', event.detail);
  }

  $: filteredByKind = $feature_names.filter((f) => {
    const info = $feature_info[f];
    const pd = $featureToPd.get(f);

    if (!pd || !shapeSelections || !info) {
      return false;
    }

    if (info.kind === 'quantitative' && pd.ordered) {
      return shapeSelections.quantitative.shapes.includes(pd.shape);
    } else if (info.subkind === 'ordinal' && pd.ordered) {
      return shapeSelections.ordinal.shapes.includes(pd.shape);
    } else if (
      (info.subkind === 'nominal' || info.subkind === 'one_hot') &&
      !pd.ordered
    ) {
      return shapeSelections.nominal.checked;
    } else {
      return false;
    }
  });
</script>

<div class="controls-container">
  <div class="bold">Feature Filters</div>

  <div>
    <div class="filter-header">
      <ToggleHeader bind:expanded={showFeatureType} title={'Type'} />
    </div>
    <div class="filter-content" class:pdp-hide={!showFeatureType}>
      <FeatureKindFilter on:changeKindFilters={onChangeKindFilters} />
    </div>
  </div>

  <div class="filter-container feature-selector-wrapper-outer">
    <div class="filter-header">
      <ToggleHeader bind:expanded={showFeatureName} title={'Name'} />
    </div>
    <div
      class="filter-content feature-selector-wrapper-inner"
      class:pdp-hide={!showFeatureName}
    >
      <FeatureNameFilter
        enabledFeatures={filteredByKind}
        on:changeNameFilters={onChangeNameFilters}
      />
    </div>
  </div>
</div>

<style>
  .controls-container {
    height: 100%;
    flex: 0 0 200px;
    min-width: 200px;
    max-width: 200px;
    padding: 0.25em;
    border-right: 1px solid var(--gray-1);

    display: flex;
    flex-direction: column;
    gap: 0.5em;
  }

  .feature-selector-wrapper-outer {
    flex: 0 1 auto;
    min-height: 0;

    display: flex;
    flex-direction: column;
  }

  .feature-selector-wrapper-inner {
    flex: 1;
    min-height: 0;
  }

  .filter-header + .filter-content {
    margin-top: 0.25em;
  }

  .filter-content {
    margin-left: 0.75em;
  }
</style>
