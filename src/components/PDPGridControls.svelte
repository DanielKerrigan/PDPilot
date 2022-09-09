<script lang="ts">
  import FeatureSelector from './FeatureSelector.svelte';
  import { num_instances_used } from '../stores';
  import { createEventDispatcher } from 'svelte';

  export let selectedFeatures: string[];

  let numIceInstances: number = 0;

  const dispatchIce = createEventDispatcher<{
    changeNumIceInstances: number;
  }>();
  $: dispatchIce('changeNumIceInstances', numIceInstances);
</script>

<div class="controls-container">
  <div class="feature-selector">
    <FeatureSelector bind:selectedFeatures />
  </div>

  <label class="label-and-input">
    <span>ICE Instances</span><input
      type="number"
      min="0"
      max={$num_instances_used}
      bind:value={numIceInstances}
      style:width="6ch"
    />
  </label>
</div>

<style>
  .controls-container {
    flex: 0 0 200px;
    min-width: 200px;
    padding: 0.25em;
    border-top: 1px solid var(--gray-1);
    border-right: 1px solid var(--gray-1);

    display: flex;
    flex-direction: column;
    gap: 1em;
  }

  .feature-selector {
    flex: 0 1 auto;
    min-height: 0;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }
</style>
