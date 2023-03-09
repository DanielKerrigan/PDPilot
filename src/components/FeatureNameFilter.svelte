<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { feature_names } from '../stores';

  export let enabledFeatures: string[];

  const dispatch = createEventDispatcher<{ changeNameFilters: string[] }>();

  let featuresChecked = true;
  let featuresCheckboxIndeterminate = false;
  let search = '';
  let selectedFeatures = $feature_names;
  let manuallyUnselected = new Set();

  function onEnabledFeaturesChange(enabledFeatures: string[]) {
    selectedFeatures = $feature_names.filter(
      (f) => enabledFeatures.includes(f) && !manuallyUnselected.has(f)
    );

    updateAllFeaturesCheckbox();
    dispatch('changeNameFilters', selectedFeatures);
  }

  $: onEnabledFeaturesChange(enabledFeatures);

  $: allFeaturesEnabled = enabledFeatures.length === $feature_names.length;

  $: featureCheckboxes = $feature_names.map((feature) => ({
    feature,
    hidden: !feature.toLocaleLowerCase().includes(search.toLocaleLowerCase()),
    disabled: !enabledFeatures.includes(feature),
  }));

  $: {
    updateAllFeaturesCheckbox();
    dispatch('changeNameFilters', selectedFeatures);
  }

  function onAllFeaturesChange() {
    if (featuresChecked) {
      selectedFeatures = $feature_names;
      featuresCheckboxIndeterminate = false;
    } else {
      selectedFeatures = [];
      featuresCheckboxIndeterminate = false;
    }
    manuallyUnselected = new Set();
  }

  function updateAllFeaturesCheckbox() {
    if (selectedFeatures.length === 0) {
      featuresChecked = false;
      featuresCheckboxIndeterminate = false;
    } else if (selectedFeatures.length === $feature_names.length) {
      featuresChecked = true;
      featuresCheckboxIndeterminate = false;
    } else if (
      selectedFeatures.length > 0 &&
      selectedFeatures.length < $feature_names.length
    ) {
      featuresChecked = true;
      featuresCheckboxIndeterminate = true;
    }
  }

  function onFeatureManuallyChanged(feature: string) {
    if (!selectedFeatures.includes(feature)) {
      manuallyUnselected.add(feature);
    } else {
      manuallyUnselected.delete(feature);
    }
  }
</script>

<div class="controls-features">
  <ul>
    <li class="fs-row">
      <input
        id="features-checkbox"
        type="checkbox"
        bind:checked={featuresChecked}
        indeterminate={featuresCheckboxIndeterminate}
        on:change={onAllFeaturesChange}
        disabled={search !== '' || !allFeaturesEnabled}
      />
      <label for="features-checkbox">All features</label>
    </li>
  </ul>

  <label class="fs-row">
    Search
    <input bind:value={search} />
  </label>

  <ul class="individual-features">
    {#each featureCheckboxes as { feature, hidden, disabled } (feature)}
      <li class="fs-row" class:hidden>
        <input
          id="{feature}-checkbox"
          type="checkbox"
          bind:group={selectedFeatures}
          name="features"
          value={feature}
          {disabled}
          on:change={() => onFeatureManuallyChanged(feature)}
        />
        <label class="pdpilot-cutoff" for="{feature}-checkbox" title={feature}
          >{feature}</label
        >
      </li>
    {/each}
  </ul>
</div>

<style>
  .controls-features {
    display: flex;
    flex-direction: column;
    max-height: 100%;
    row-gap: 0.25em;
  }

  ul {
    list-style: none;
  }

  .fs-row {
    display: flex;
    align-items: center;
    column-gap: 0.25em;
  }

  input {
    min-width: 0;
  }

  .fs-row label {
    flex: 1;
  }

  .individual-features {
    flex: 0 1 auto;
    overflow-y: scroll;
    min-height: 0;
  }

  .hidden {
    display: none;
  }
</style>
