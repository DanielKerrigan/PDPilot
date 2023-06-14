<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { feature_names } from '../stores';

  export let enabledFeatures: string[];
  // IDs used for linking label to checkboxes must be unique
  export let idPrefix: string;

  const dispatch = createEventDispatcher<{ changeNameFilters: string[] }>();

  let search = '';
  let selectedFeatures: string[] = [];

  export function clear() {
    selectedFeatures = [];
  }

  function onEnabledFeaturesChange(enabledFeatures: string[]) {
    const allEnabled = enabledFeatures.length === $feature_names.length;
    selectedFeatures = allEnabled ? [] : enabledFeatures;

    dispatchSelections(selectedFeatures, allEnabled);
  }

  $: onEnabledFeaturesChange(enabledFeatures);

  $: featureCheckboxes = $feature_names.map((feature) => ({
    feature,
    hidden: !feature.toLocaleLowerCase().includes(search.toLocaleLowerCase()),
    disabled: !enabledFeatures.includes(feature),
  }));

  // if all of the features are checked, then uncheck all of them
  $: if (selectedFeatures.length === $feature_names.length) {
    selectedFeatures = [];
  }

  $: dispatchSelections(
    selectedFeatures,
    enabledFeatures.length === $feature_names.length
  );

  function dispatchSelections(feats: string[], allEnabled: boolean) {
    // if nothing is selected and all features are enabled,
    // then the default is that all are selected
    if (feats.length === 0 && allEnabled) {
      dispatch('changeNameFilters', $feature_names);
    } else {
      dispatch('changeNameFilters', feats);
    }
  }
</script>

<div class="controls-features">
  <label class="fs-row">
    Search
    <input bind:value={search} />
  </label>

  <ul class="individual-features">
    {#each featureCheckboxes as { feature, hidden, disabled } (feature)}
      <li class="fs-row" class:hidden>
        <input
          id="{idPrefix}-{feature}-checkbox"
          type="checkbox"
          bind:group={selectedFeatures}
          name="features"
          value={feature}
          {disabled}
        />
        <label
          class="pdpilot-cutoff"
          class:disabled-feature-label={disabled}
          for="{idPrefix}-{feature}-checkbox"
          title={feature}>{feature}</label
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
    overflow-y: auto;
    min-height: 0;
  }

  .hidden {
    display: none;
  }

  .disabled-feature-label {
    color: var(--gray-5);
    cursor: not-allowed;
  }
</style>
