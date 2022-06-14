<script lang="ts">
  import PDPGroup from './PDPGroup.svelte';
  import { single_pdps, double_pdps } from '../stores';
  import * as d3 from 'd3';

  let singleExpanded = true;
  let doubleExpanded = true;

  $: minPrediction = d3.min($single_pdps, pdp => d3.min(pdp.values, d => d.avg_pred)) ?? 0;
  $: maxPrediction = d3.max($single_pdps, pdp => d3.max(pdp.values, d => d.avg_pred)) ?? 0;

  let predictionExtent: [number, number];
  $: predictionExtent = d3.scaleLinear().domain([minPrediction, maxPrediction]).nice().domain() as [number, number];
</script>

<div class='main-container'>
  <PDPGroup
    title={'Single feature'}
    data={$single_pdps}
    predictionExtent={predictionExtent}
    showColorLegend={false}
    bind:expanded={singleExpanded}
    otherSectionCollapsed={!doubleExpanded}
  />

  <PDPGroup
    title={'Double feature'}
    data={$double_pdps}
    predictionExtent={predictionExtent}
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