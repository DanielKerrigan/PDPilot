<script lang="ts">
  import { features } from '../stores';

  export let localSelectedFeatures: string[];

  let featuresChecked = false;
  let featuresCheckboxIndeterminate = false;

  function onAllFeaturesChange() {
    if (featuresChecked) {
      localSelectedFeatures = $features;
      featuresCheckboxIndeterminate = false;
    } else {
      localSelectedFeatures = [];
      featuresCheckboxIndeterminate = false;
    }
  }

  function onFeatureChange() {
    if (localSelectedFeatures.length === 0 && featuresChecked) {
      featuresChecked = false;
      featuresCheckboxIndeterminate = false;
    } else if (
      localSelectedFeatures.length === $features.length &&
      !featuresChecked
    ) {
      featuresChecked = true;
      featuresCheckboxIndeterminate = false;
    } else if (
      localSelectedFeatures.length > 0 &&
      localSelectedFeatures.length < $features.length
    ) {
      featuresChecked = true;
      featuresCheckboxIndeterminate = true;
    }
  }
</script>

<div class="controls-features">
  <ul>
    <li>
      <label class="bold">
        <input
          type="checkbox"
          bind:checked={featuresChecked}
          indeterminate={featuresCheckboxIndeterminate}
          on:change={onAllFeaturesChange}
        />
        <span>Features</span>
      </label>
    </li>
    {#each $features as feature}
      <li>
        <label>
          <input
            type="checkbox"
            bind:group={localSelectedFeatures}
            name="features"
            value={feature}
            on:change={onFeatureChange}
          />
          <span>{feature}</span>
        </label>
      </li>
    {/each}
  </ul>
</div>

<style>
  ul {
    list-style: none;
  }

  /* https://stackoverflow.com/a/494922/5016634 */
  label span,
  label input {
    vertical-align: middle;
  }
</style>
