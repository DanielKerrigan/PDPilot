<script lang="ts">
  import FeatureNameFilter from './FeatureNameFilter.svelte';
  import ToggleHeader from './ToggleHeader.svelte';
  import { createEventDispatcher } from 'svelte';
  import { feature_names } from '../stores';

  const dispatch = createEventDispatcher<{
    changeFilters: {
      features: string[];
      op: 'and' | 'or';
    };
  }>();

  let featureNameFilter: FeatureNameFilter;

  let showFeatureName = true;

  let op: 'and' | 'or' = 'and';
  let selectedFeatures: string[] = $feature_names;

  function onChangeNameFilters(event: CustomEvent<string[]>) {
    dispatch('changeFilters', {
      features: event.detail,
      op: op,
    });
    selectedFeatures = event.detail;
  }

  function onChangeOp() {
    dispatch('changeFilters', {
      features: selectedFeatures,
      op: op,
    });
  }

  function clearFilters() {
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

  <div class="filter-container feature-selector-wrapper-outer">
    <div class="filter-header">
      <ToggleHeader bind:expanded={showFeatureName} title={'Name'} />
    </div>
    <div
      class="filter-content feature-selector-wrapper-middle"
      class:pdp-hide={!showFeatureName}
    >
      <div class="two-way-filter-radio">
        <div>Plots must contain</div>
        <label>
          <input
            type="radio"
            bind:group={op}
            name="op"
            value="or"
            on:change={onChangeOp}
          />
          1+ selected feature
        </label>
        <label>
          <input
            type="radio"
            bind:group={op}
            name="op"
            value="and"
            on:change={onChangeOp}
          />
          2 selected features
        </label>
      </div>

      <hr />

      <div class="feature-selector-wrapper-inner">
        <FeatureNameFilter
          bind:this={featureNameFilter}
          enabledFeatures={$feature_names}
          on:changeNameFilters={onChangeNameFilters}
          idPrefix={'pdpilot-two'}
        />
      </div>
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

  .feature-selector-wrapper-middle {
    flex: 1;
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

  hr {
    margin: 0.75em 0;
    border: 0;
    height: 1px;
    background: var(--gray-2);
  }

  .two-way-filter-radio {
    display: flex;
    flex-direction: column;
  }
</style>
