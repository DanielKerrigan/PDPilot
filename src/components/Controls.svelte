<script lang="ts">
  import FeatureSelector from "./FeatureSelector.svelte";
  import Parameters from "./Parameters.svelte";
  import PlotButton from "./PlotButton.svelte";
  import { num_instances_used, resolution } from '../stores';

  let localSelectedFeatures: string[] = [];
  let localResolution: number = $resolution;
  let localNumInstances: number = $num_instances_used;
</script>

<div class="controls-container">
  <div>
    <FeatureSelector bind:localSelectedFeatures={localSelectedFeatures}/>
  </div>
  <div>
    <Parameters bind:localResolution={localResolution} bind:localNumInstances={localNumInstances}/>
  </div>
  <div>
    <PlotButton {localSelectedFeatures} {localResolution} {localNumInstances}/>
  </div>
</div>

<style>
  .controls-container {
    flex: 0 0 200px;
    min-width: 200px;
    padding: 0.25em;
    background-color: var(--light-gray);
    border: 1px solid var(--medium-gray);

    display: flex;
    flex-direction: column;
    gap: 1em;
  }
</style>