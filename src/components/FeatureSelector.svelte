<script lang="ts">
  import { selected_features, features } from '../stores';

  let featuresChecked: boolean = true;
  let featuresCheckboxIndeterminate: boolean = false;
  let search: string = '';

  $: $selected_features = $features;
  $: featureCheckboxes = $features.map((feature) => ({
    feature,
    hidden: !feature.includes(search),
  }));

  function onAllFeaturesChange() {
    if (featuresChecked) {
      $selected_features = $features;
      featuresCheckboxIndeterminate = false;
    } else {
      $selected_features = [];
      featuresCheckboxIndeterminate = false;
    }
  }

  function onFeatureChange() {
    if ($selected_features.length === 0) {
      featuresChecked = false;
      featuresCheckboxIndeterminate = false;
    } else if ($selected_features.length === $features.length) {
      featuresChecked = true;
      featuresCheckboxIndeterminate = false;
    } else if (
      $selected_features.length > 0 &&
      $selected_features.length < $features.length
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
          bind:group={$selected_features}
          name="features"
          value={feature}
          on:change={onFeatureChange}
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
