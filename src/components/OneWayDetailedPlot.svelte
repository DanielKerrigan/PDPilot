<script lang="ts">
  import type { OneWayPD, FeatureInfo } from '../types';
  import {
    detailedScaleLocally,
    detailedICELevel,
    detailedContextKind,
    isClassification,
    labelExtent,
    dataset,
    labels,
    num_instances,
    highlighted_indices,
  } from '../stores';
  import PDP from './PDP.svelte';
  import ClusterDescriptions from './vis/ice-clusters/ClusterDescriptions.svelte';
  import Scatterplot from './vis/distribution/Scatterplot.svelte';
  import { getClustering } from '../utils';

  export let pd: OneWayPD;
  export let featureInfo: FeatureInfo;
  export let width: number;
  export let height: number;

  $: halfWidth = width / 2;

  const marginalPlotHeight = 50;

  // cluster description interaction

  let indices: number[] | null = null;

  function onFilterIndices(event: CustomEvent<number[]>) {
    indices = event.detail;
  }

  $: if ($detailedContextKind !== 'cluster-descriptions') {
    indices = null;
  }

  $: if (
    $detailedICELevel !== 'cluster-lines' &&
    $detailedContextKind === 'cluster-descriptions'
  ) {
    $detailedContextKind = 'scatterplot';
  }
</script>

<div class="one-way-pdp-grid">
  {#if $detailedICELevel === 'cluster-lines' && pd.ice.num_clusters === 1}
    <div class="pdpilot-no-clusters-message">
      This feature does not have any distinct clusters of ICE lines.
    </div>
  {:else}
    <div style:flex="1">
      <PDP
        {pd}
        width={$detailedContextKind === 'none' ? width : halfWidth}
        {height}
        scaleLocally={$detailedScaleLocally}
        showMarginalDistribution={false}
        marginTop={10}
        marginalPlotHeight={0}
        iceLevel={$detailedICELevel}
        {indices}
        allowBrushing={true}
        showColorLegend={false}
        showTitle={true}
      />
    </div>

    {#if $detailedContextKind === 'cluster-descriptions'}
      <div style:flex="1">
        <ClusterDescriptions
          on:filter={onFilterIndices}
          {pd}
          features={getClustering(pd).interacting_features}
        />
      </div>
    {:else if $detailedContextKind === 'scatterplot'}
      <div style:flex="1">
        <Scatterplot
          width={halfWidth}
          {height}
          xValues={$dataset[pd.x_feature]}
          yValues={$labels}
          colorValues={Array.from({ length: $num_instances }, (_, i) =>
            $highlighted_indices.includes(i) ? 1 : 0
          )}
          xKind={featureInfo.kind}
          yKind={$isClassification ? 'categorical' : 'quantitative'}
          colorKind={'categorical'}
          xDomain={featureInfo.kind === 'categorical'
            ? pd.x_values
            : [pd.x_values[0], pd.x_values[pd.x_values.length - 1]]}
          yDomain={$labelExtent}
          colorDomain={[0, 1]}
          colorScheme={'highlight'}
          xLabel={pd.x_feature}
          yLabel={'Ground Truth'}
          colorLabel=""
          xAxisIntegerOnly={featureInfo.subkind === 'discrete'}
          yAxisIntegerOnly={false}
          xAxisValueMap={'value_map' in featureInfo
            ? featureInfo.value_map
            : {}}
          yAxisValueMap={{}}
          xDistribution={featureInfo.distribution}
          yDistribution={null}
          opacity={0.5}
          allowBrushing={true}
          showMarginalDistribution={true}
          marginTop={marginalPlotHeight + 3}
          marginRight={marginalPlotHeight + 3}
          {marginalPlotHeight}
          title="Ground Truth Labels vs. Feature Values"
        />
      </div>
    {/if}
  {/if}
</div>

<style>
  .one-way-pdp-grid {
    display: flex;
    width: 100%;
    height: 100%;
  }

  .pdpilot-no-clusters-message {
    flex: 1;
    text-align: center;
    align-self: center;
  }
</style>
