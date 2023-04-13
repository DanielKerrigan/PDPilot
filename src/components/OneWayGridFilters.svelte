<script lang="ts">
  import FeatureNameFilter from './FeatureNameFilter.svelte';
  import FeatureKindFilter from './FeatureKindFilter.svelte';
  import ToggleHeader from './ToggleHeader.svelte';
  import { feature_names, featureToPd } from '../stores';
  import type { ShapeSelections } from '../types';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ changeFilters: string[] }>();

  let featureKindFilter: FeatureKindFilter;
  let featureNameFilter: FeatureNameFilter;

  let showFeatureType = true;
  let showFeatureName = true;

  let shapeSelections: ShapeSelections;

  function onChangeKindFilters(event: CustomEvent<ShapeSelections>) {
    shapeSelections = event.detail;
  }

  // we could just pass this up
  function onChangeNameFilters(event: CustomEvent<string[]>) {
    dispatch('changeFilters', event.detail);
  }

  $: filteredByKind = $feature_names.filter((f) => {
    const pd = $featureToPd.get(f);

    if (!pd || !shapeSelections) {
      return false;
    }

    if (pd.ordered) {
      return shapeSelections.ordered.shapes.includes(pd.shape);
    } else {
      return shapeSelections.nominal.checked;
    }
  });

  function clearFilters() {
    if (featureKindFilter) {
      featureKindFilter.clear();
    }

    if (featureNameFilter) {
      featureNameFilter.clear();
    }
  }
</script>

<div class="controls-container">
  <div class="pdpilot-bold">Feature Filters</div>

  <button style:align-self="start" on:click={clearFilters}>
    Clear Filters
  </button>

  <div>
    <div class="filter-header">
      <ToggleHeader bind:expanded={showFeatureType} title={'Type'} />
    </div>
    <div class="filter-content" class:pdp-hide={!showFeatureType}>
      <FeatureKindFilter
        bind:this={featureKindFilter}
        on:changeKindFilters={onChangeKindFilters}
      />
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
        bind:this={featureNameFilter}
        enabledFeatures={filteredByKind}
        on:changeNameFilters={onChangeNameFilters}
        idPrefix={'pdpilot-one'}
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
