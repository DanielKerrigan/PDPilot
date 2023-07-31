<script lang="ts">
  import type {
    OneWayPD,
    FeatureInfo,
    ICELevel,
    OneWayDetailedContextKind,
  } from '../types';
  import {
    detailedScaleLocally,
    detailedICELevel,
    detailedContextKind,
    isClassification,
    labelExtent,
    dataset,
    labels,
    num_instances,
    highlightedIndicesSet,
  } from '../stores';
  import PDP from './PDP.svelte';
  import ClusterDescriptions from './vis/ice-clusters/ClusterDescriptions.svelte';
  import Scatterplot from './vis/distribution/Scatterplot.svelte';
  import { getClustering } from '../utils';
  import SegmentedButton from './SegmentedButton.svelte';

  export let pd: OneWayPD;
  export let featureInfo: FeatureInfo;

  // sizes

  let contentRectICE: DOMRectReadOnly | undefined | null;
  $: iceWidth = contentRectICE ? contentRectICE.width : 0;
  $: iceHeight = contentRectICE ? contentRectICE.height : 0;

  let contentRectContext: DOMRectReadOnly | undefined | null;
  $: contextWidth = contentRectContext ? contentRectContext.width : 0;
  $: contextHeight = contentRectContext ? contentRectContext.height : 0;

  const marginalPlotHeight = 50;

  const iceLevels: { value: ICELevel; label: string; enabled: true }[] = [
    { value: 'lines', label: 'Standard', enabled: true },
    { value: 'centered-lines', label: 'Centered', enabled: true },
    { value: 'cluster-lines', label: 'Clusters', enabled: true },
  ];

  let contextOptions: {
    value: OneWayDetailedContextKind;
    label: string;
    enabled: boolean;
  }[] = [];

  $: contextOptions = [
    { value: 'scatterplot', label: 'Feature vs. Label', enabled: true },
    {
      value: 'cluster-descriptions',
      label: 'Cluster Descriptions',
      enabled: $detailedICELevel === 'cluster-lines',
    },
  ];

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

<div class="one-way-detailed-pdp-container">
  {#if $detailedICELevel === 'cluster-lines' && pd.ice.num_clusters === 1}
    <div class="pdpilot-no-clusters-message">
      This feature does not have enough distinct clusters of ICE lines.
    </div>
  {:else}
    <div class="pdpilot-half">
      <div
        class="pdpilot-half-header"
        style:margin-bottom="{$detailedICELevel === 'cluster-lines'
          ? 0.25
          : 0.5}em"
      >
        <SegmentedButton
          segments={iceLevels}
          title={'ICE Plot'}
          bind:selectedValue={$detailedICELevel}
        />
      </div>

      <div class="pdpilot-half-vis" bind:contentRect={contentRectICE}>
        <!--
          in cluster lines, marginTop specifies the margin beneath the header
          and above all of the charts, not the margin above each individual plot.
        -->
        <PDP
          {pd}
          width={iceWidth}
          height={iceHeight}
          scaleLocally={$detailedScaleLocally}
          showMarginalDistribution={false}
          marginTop={$detailedICELevel === 'cluster-lines' ? 0 : 10}
          marginalPlotHeight={0}
          iceLevel={$detailedICELevel}
          {indices}
          allowBrushing={true}
          showColorLegend={false}
        />
      </div>
    </div>

    <div class="pdpilot-vertical-divider" />

    <div class="pdpilot-half">
      <div
        class="pdpilot-half-header"
        style:margin-bottom="{$detailedContextKind === 'cluster-descriptions'
          ? 0.25
          : 0.5}em"
      >
        <SegmentedButton
          segments={contextOptions}
          title={'Context'}
          bind:selectedValue={$detailedContextKind}
        />
      </div>
      <div class="pdpilot-half-vis" bind:contentRect={contentRectContext}>
        {#if $detailedContextKind === 'cluster-descriptions'}
          <ClusterDescriptions
            on:filter={onFilterIndices}
            {pd}
            features={getClustering(pd).interacting_features}
          />
        {:else if $detailedContextKind === 'scatterplot'}
          <Scatterplot
            width={contextWidth}
            height={contextHeight}
            xValues={$dataset[pd.x_feature]}
            yValues={$labels}
            colorValues={Array.from({ length: $num_instances }, (_, i) =>
              $highlightedIndicesSet.has(i) ? 1 : 0
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
            yLabel={'Ground truth'}
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
          />
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .one-way-detailed-pdp-container {
    display: flex;
    width: 100%;
    height: 100%;
  }

  .pdpilot-no-clusters-message {
    flex: 1;
    text-align: center;
    align-self: center;
  }

  .pdpilot-half {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .pdpilot-half-vis {
    flex: 1;
  }

  .pdpilot-vertical-divider {
    width: 1px;
    margin: 0 1em;
    background-color: var(--gray-1);
  }
</style>
