<script lang="ts">
  import FeatureSelector from './FeatureSelector.svelte';

  export let selectedFeatures: string[];
</script>

<div class="controls-container">
  <div class="feature-selector">
    <FeatureSelector bind:selectedFeatures />
  </div>
</div>

<style>
  .controls-container {
    height: 100%;
    flex: 0 0 200px;
    min-width: 200px;
    padding: 0.25em;
    border-right: 1px solid var(--gray-1);

    display: flex;
    flex-direction: column;
    gap: 1em;
  }

  .feature-selector {
    flex: 0 1 auto;
    min-height: 0;
  }
</style>
