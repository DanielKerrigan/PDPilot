<script lang="ts">
  import FeatureNameFilter from './FeatureNameFilter.svelte';
  import ToggleHeader from './ToggleHeader.svelte';
  import { createEventDispatcher } from 'svelte';
  import { feature_names } from '../stores';

  const dispatch = createEventDispatcher<{ changeFilters: string[] }>();

  let showFeatureName = true;

  function onChangeNameFilters(event: CustomEvent<string[]>) {
    dispatch('changeFilters', event.detail);
  }
</script>

<div class="controls-container">
  <div class="pdpilot-bold">Feature Filters</div>

  <div class="filter-container feature-selector-wrapper-outer">
    <div class="filter-header">
      <ToggleHeader bind:expanded={showFeatureName} title={'Name'} />
    </div>
    <div
      class="filter-content feature-selector-wrapper-inner"
      class:pdp-hide={!showFeatureName}
    >
      <FeatureNameFilter
        enabledFeatures={$feature_names}
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
