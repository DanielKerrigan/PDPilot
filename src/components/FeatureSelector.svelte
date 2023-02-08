<script lang="ts">
  import { feature_names } from '../stores';

  export let selectedFeatures: string[];

  let featuresChecked = true;
  let featuresCheckboxIndeterminate = false;
  let search = '';

  $: featureCheckboxes = $feature_names.map((feature) => ({
    feature,
    hidden: !feature.includes(search),
  }));

  $: selectedFeatures, onFeatureChange();

  function onAllFeaturesChange() {
    if (featuresChecked) {
      selectedFeatures = $feature_names;
      featuresCheckboxIndeterminate = false;
    } else {
      selectedFeatures = [];
      featuresCheckboxIndeterminate = false;
    }
  }

  function onFeatureChange() {
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
        disabled={search !== ''}
      />
      <label class="bold" for="features-checkbox">Features</label>
    </li>
  </ul>

  <label class="fs-row">
    Search
    <input bind:value={search} />
  </label>

  <ul class="individual-features">
    {#each featureCheckboxes as { feature, hidden } (feature)}
      <li class="fs-row" class:hidden>
        <input
          id="{feature}-checkbox"
          type="checkbox"
          bind:group={selectedFeatures}
          name="features"
          value={feature}
        />
        <label class="cutoff" for="{feature}-checkbox" title={feature}
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
