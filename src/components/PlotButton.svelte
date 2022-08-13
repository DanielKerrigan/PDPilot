<script lang="ts">
  import {
    num_instances_used,
    plot_button_clicked,
    resolution,
    selected_features,
    include_double_pdps,
  } from '../stores';
  import { areArraysEqual } from '../utils';

  export let localSelectedFeatures: string[];
  export let localResolution: number;
  export let localNumInstances: number;
  export let localIncludeDouble: boolean;

  $: disabled =
    localSelectedFeatures.length === 0 ||
    (areArraysEqual(localSelectedFeatures, $selected_features) &&
      localResolution === $resolution &&
      localNumInstances === $num_instances_used &&
      localIncludeDouble === $include_double_pdps);

  function plotButtonClicked() {
    selected_features.set(localSelectedFeatures);
    resolution.set(localResolution);
    num_instances_used.set(localNumInstances);
    include_double_pdps.set(localIncludeDouble);
    plot_button_clicked.update((x) => x + 1);
  }
</script>

<button {disabled} on:click={plotButtonClicked}>Plot</button>

<style>
</style>
