<script lang="ts">
  import PDPGroup from './PDPGroup.svelte';
  import { single_pdps, double_pdps } from '../stores';
  import { scaleLinear } from 'd3-scale';
  import { min, max } from 'd3-array';

  let singleExpanded = true;
  let doubleExpanded = true;

  $: minPrediction =
    min($single_pdps, (pdp) => min(pdp.values, (d) => d.avg_pred)) ?? 0;
  $: maxPrediction =
    max($single_pdps, (pdp) => max(pdp.values, (d) => d.avg_pred)) ?? 0;

  let predictionExtent: [number, number];
  $: predictionExtent = scaleLinear()
    .domain([minPrediction, maxPrediction])
    .nice()
    .domain() as [number, number];
</script>

<div class="main-container">
  <PDPGroup
    title={'Single feature'}
    data={$single_pdps}
    {predictionExtent}
    showColorLegend={false}
    bind:expanded={singleExpanded}
    otherSectionCollapsed={!doubleExpanded}
  />

  <PDPGroup
    title={'Double feature'}
    data={$double_pdps}
    {predictionExtent}
    showColorLegend={true}
    bind:expanded={doubleExpanded}
    otherSectionCollapsed={!singleExpanded}
  />
</div>

<style>
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-bottom: 1px solid var(--medium-gray);
  }
</style>
