<script lang="ts">
  import type { FeatureInfo, TwoWayPD } from '../types';
  import {
    detailedScaleLocally,
    isClassification,
    labelExtent,
    feature_info,
    dataset,
    labels,
  } from '../stores';
  import PDP from './PDP.svelte';
  import Scatterplot from './vis/distribution/Scatterplot.svelte';

  export let pd: TwoWayPD;
  export let xFeatureInfo: FeatureInfo;
  export let yFeatureInfo: FeatureInfo;

  // sizes

  let contentRect: DOMRectReadOnly | undefined | null;
  $: width = contentRect ? contentRect.width : 0;
  $: height = contentRect ? contentRect.height : 0;
  $: thirdWidth = width / 3;

  const marginalPlotHeight = 50;
</script>

<div class="two-way-pdp-grid" bind:contentRect>
  <div style:grid-area="two-way-interaction">
    <PDP
      {pd}
      width={thirdWidth}
      {height}
      scaleLocally={$detailedScaleLocally}
      showMarginalPdp={true}
      marginTop={marginalPlotHeight + 1}
      marginRight={marginalPlotHeight + 1}
      {marginalPlotHeight}
      iceLevel="lines"
      colorShows="interactions"
      showColorLegend={true}
      colorLegendTitle="Interactions"
    />
  </div>

  <div style:grid-area="two-way-pdp">
    <PDP
      {pd}
      width={thirdWidth}
      {height}
      scaleLocally={$detailedScaleLocally}
      showMarginalPdp={true}
      marginTop={marginalPlotHeight + 1}
      marginRight={marginalPlotHeight + 1}
      {marginalPlotHeight}
      iceLevel={'lines'}
      showColorLegend={true}
      colorLegendTitle="Predictions"
    />
  </div>

  <div style:grid-area="scatter">
    <Scatterplot
      width={thirdWidth}
      {height}
      xValues={$dataset[pd.x_feature]}
      yValues={$dataset[pd.y_feature]}
      colorValues={$labels}
      xKind={xFeatureInfo.kind}
      yKind={yFeatureInfo.kind}
      colorKind={$isClassification ? 'categorical' : 'quantitative'}
      xDomain={xFeatureInfo.kind === 'categorical'
        ? pd.x_axis
        : [pd.x_axis[0], pd.x_axis[pd.x_axis.length - 1]]}
      yDomain={$feature_info[pd.y_feature].kind === 'categorical'
        ? pd.y_axis
        : [pd.y_axis[0], pd.y_axis[pd.y_axis.length - 1]]}
      colorDomain={$labelExtent}
      colorScheme={$isClassification ? 'classes' : 'sequential'}
      xLabel={pd.x_feature}
      yLabel={pd.y_feature}
      colorLabel="Ground truth"
      xAxisIntegerOnly={xFeatureInfo.subkind === 'discrete'}
      yAxisIntegerOnly={yFeatureInfo.subkind === 'discrete'}
      xAxisValueMap={'value_map' in xFeatureInfo ? xFeatureInfo.value_map : {}}
      yAxisValueMap={'value_map' in yFeatureInfo ? yFeatureInfo.value_map : {}}
      xDistribution={xFeatureInfo.distribution}
      yDistribution={yFeatureInfo.distribution}
      opacity={1}
      allowBrushing={false}
      showMarginalDistribution={true}
      marginTop={marginalPlotHeight + 3}
      marginRight={marginalPlotHeight + 3}
      {marginalPlotHeight}
    />
  </div>
</div>

<style>
  .two-way-pdp-grid {
    display: grid;
    width: 100%;
    height: 100%;
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-areas: 'two-way-interaction two-way-pdp scatter';
  }
</style>
