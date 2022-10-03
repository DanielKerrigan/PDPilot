<script lang="ts">
  import FeatureSelector from './FeatureSelector.svelte';
  import { createEventDispatcher } from 'svelte';

  export let selectedFeatures: string[];

  let showIceClusters: boolean = false;

  const dispatchClusters = createEventDispatcher<{
    changeShowIceClusters: boolean;
  }>();
  $: dispatchClusters('changeShowIceClusters', showIceClusters);
</script>

<div class="controls-container">
  <div class="feature-selector">
    <FeatureSelector bind:selectedFeatures />
  </div>

  <label class="label-and-input">
    <span>Show ICE Clusters</span><input
      type="checkbox"
      bind:checked={showIceClusters}
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
