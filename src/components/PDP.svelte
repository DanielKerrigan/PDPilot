<script lang="ts">
  import type {
    SinglePDPData,
    DoublePDPData,
    MarginalDistribution,
  } from '../types';
  import { marginal_distributions } from '../stores';
  import LineChart from './vis/one_way/LineChart.svelte';
  import DotPlot from './vis/one_way/DotPlot.svelte';
  import QuantitativeHeatmap from './vis/two_way/QuantitativeHeatmap.svelte';
  import MixedHeatmap from './vis/two_way/MixedHeatmap.svelte';
  import CategoricalHeatmap from './vis/two_way/CategoricalHeatmap.svelte';

  export let pdp: SinglePDPData | DoublePDPData;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;
  export let showMarginalDistribution: boolean;
  export let numIceInstances: number = 0;
  export let showInteractions: boolean = false;
  export let showColorLegend: boolean = false;

  let mdx: MarginalDistribution | null = null;
  let mdy: MarginalDistribution | null = null;

  $: if (showMarginalDistribution) {
    mdx = $marginal_distributions[pdp.x_feature] ?? null;
    mdy =
      pdp.num_features === 2 ? $marginal_distributions[pdp.y_feature] : null;
  } else {
    mdx = null;
    mdy = null;
  }
</script>

{#if width > 0 && height > 0}
  {#if pdp.num_features === 1}
    {#if pdp.kind === 'quantitative' && (mdx === null || mdx.kind === 'quantitative')}
      <LineChart
        {width}
        {height}
        {pdp}
        {scaleLocally}
        {showTrendLine}
        {numIceInstances}
        marginalDistributionX={mdx}
      />
    {:else if pdp.kind === 'categorical' && (mdx === null || mdx.kind === 'categorical')}
      <DotPlot
        {width}
        {height}
        {pdp}
        {scaleLocally}
        {numIceInstances}
        marginalDistributionX={mdx}
      />
    {/if}
  {:else if pdp.num_features === 2}
    {#if pdp.kind === 'quantitative' && (mdx === null || mdx.kind === 'quantitative') && (mdy === null || mdy.kind === 'quantitative')}
      <QuantitativeHeatmap
        {width}
        {height}
        {pdp}
        {globalColor}
        {scaleLocally}
        marginalDistributionX={mdx}
        marginalDistributionY={mdy}
        {showInteractions}
        {showColorLegend}
      />
    {:else if pdp.kind === 'mixed' && (mdx === null || mdx.kind === 'quantitative') && (mdy === null || mdy.kind === 'categorical')}
      <MixedHeatmap
        {width}
        {height}
        {pdp}
        {globalColor}
        {scaleLocally}
        marginalDistributionX={mdx}
        marginalDistributionY={mdy}
        {showInteractions}
        {showColorLegend}
      />
    {:else if pdp.kind === 'categorical' && (mdx === null || mdx.kind === 'categorical') && (mdy === null || mdy.kind === 'categorical')}
      <CategoricalHeatmap
        {width}
        {height}
        {pdp}
        {globalColor}
        {scaleLocally}
        marginalDistributionX={mdx}
        marginalDistributionY={mdy}
        {showInteractions}
        {showColorLegend}
      />
    {/if}
  {/if}
{/if}

<style>
</style>
