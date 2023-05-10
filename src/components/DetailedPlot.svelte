<script lang="ts">
  import type { OneWayPD, ICELevel, TwoWayPD } from '../types';
  import { onMount } from 'svelte';
  import {
    two_way_pds,
    feature_names,
    two_way_to_calculate,
    detailedFeature1,
    detailedFeature2,
    detailedScaleLocally,
    detailedICELevel,
    featureToPd,
    detailedContextKind,
  } from '../stores';
  import PDP from './PDP.svelte';
  import ClusterDescriptions from './vis/ice-clusters/ClusterDescriptions.svelte';
  import FeatureVsFeature from './vis/two-way/FeatureVsFeature.svelte';
  import FeatureVsLabels from './vis/one-way/FeatureVsLabels.svelte';

  let pd: OneWayPD | TwoWayPD | null = null;

  const marginalPlotHeight = 50;

  // changing features

  function onChangeFeature() {
    if ($detailedFeature1 === $detailedFeature2) {
      $detailedFeature2 = '';
    }

    if ($detailedFeature1 === '' && $detailedFeature2 !== '') {
      $detailedFeature1 = $detailedFeature2;
      $detailedFeature2 = '';
    }

    if ($detailedFeature2 === '') {
      pd = $featureToPd.get($detailedFeature1) ?? null;
    } else {
      pd =
        $two_way_pds.find(
          (d) =>
            (d.x_feature === $detailedFeature1 &&
              d.y_feature === $detailedFeature2) ||
            (d.x_feature === $detailedFeature2 &&
              d.y_feature === $detailedFeature1)
        ) ?? null;
    }
  }

  function computeTwoWayPd() {
    $two_way_to_calculate = [$detailedFeature1, $detailedFeature2];
  }

  function getComputedTwoWayPd() {
    const foundPd = $two_way_pds.find(
      (d) =>
        (d.x_feature === $two_way_to_calculate[0] &&
          d.y_feature === $two_way_to_calculate[1]) ||
        (d.x_feature === $two_way_to_calculate[1] &&
          d.y_feature === $two_way_to_calculate[0])
    );

    if (foundPd) {
      if (
        $two_way_to_calculate.length === 2 &&
        $two_way_to_calculate[0] === $detailedFeature1 &&
        $two_way_to_calculate[1] === $detailedFeature2
      ) {
        pd = foundPd;
      }
      $two_way_to_calculate = [];
    }
  }

  $: $detailedFeature1, $detailedFeature2, onChangeFeature();

  $: if ($two_way_pds) {
    getComputedTwoWayPd();
  }

  // one-way PDPs

  let oneWayPD1: OneWayPD | null = null;
  let oneWayPD2: OneWayPD | null = null;

  $: if (pd && pd.num_features === 2) {
    // sort alphabetically so that they don't change positions when flipping axis
    let feature1 = pd.x_feature < pd.y_feature ? pd.x_feature : pd.y_feature;
    let feature2 = pd.x_feature > pd.y_feature ? pd.x_feature : pd.y_feature;
    oneWayPD1 = $featureToPd.get(feature1) ?? null;
    oneWayPD2 = $featureToPd.get(feature2) ?? null;
  }

  const iceLevels: { value: ICELevel; title: string }[] = [
    { value: 'lines', title: 'Standard' },
    { value: 'centered-lines', title: 'Centered' },
    { value: 'cluster-lines', title: 'Clusters' },
  ];

  // sizes

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  $: halfWidth = gridWidth / 2;
  $: thirdWidth = gridWidth / 3;

  onMount(() => {
    // Adapted from https://blog.sethcorker.com/question/how-do-you-use-the-resize-observer-api-in-svelte/
    // and https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver
    const resizeObserver = new ResizeObserver(
      (entries: ResizeObserverEntry[]) => {
        if (entries.length !== 1) {
          return;
        }

        const entry: ResizeObserverEntry = entries[0];

        if (entry.contentBoxSize) {
          const contentBoxSize = Array.isArray(entry.contentBoxSize)
            ? entry.contentBoxSize[0]
            : entry.contentBoxSize;

          gridWidth = contentBoxSize.inlineSize;
          gridHeight = contentBoxSize.blockSize;
        } else {
          gridWidth = entry.contentRect.width;
          gridHeight = entry.contentRect.height;
        }
      }
    );

    resizeObserver.observe(div);

    return () => resizeObserver.unobserve(div);
  });

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

  // swap x and y axes in two-way plot

  function swapAxes() {
    if (!pd || pd.num_features === 1) {
      return;
    }

    Object.assign(pd, {
      x_feature: pd.y_feature,
      x_axis: pd.y_axis,
      x_values: pd.y_values,
      y_feature: pd.x_feature,
      y_axis: pd.x_axis,
      y_values: pd.x_values,
    });
    pd = pd;
    $two_way_pds = $two_way_pds;
  }
</script>

<div class="zoomed-pdp-container">
  <div class="zoomed-pdp-header">
    <div class="feature-selects">
      <label>
        <span>Feat. 1</span>
        <select bind:value={$detailedFeature1}>
          <option value="" />
          {#each $feature_names as feature}
            <option value={feature}>{feature}</option>
          {/each}
        </select>
      </label>

      <label>
        <span>Feat. 2</span>
        <select bind:value={$detailedFeature2}>
          <option value="" />
          {#each $feature_names as feature}
            <option value={feature}>{feature}</option>
          {/each}
        </select>
      </label>
    </div>

    {#if pd}
      {#if pd.num_features === 1}
        <!-- <label class="label-and-input">
          <input type="checkbox" bind:checked={$detailedShowDistributions} />
          {pd.num_features === 1 ? 'Distribution' : 'Distributions'}
        </label> -->
        <label class="label-and-input">
          Plot
          <select bind:value={$detailedICELevel}>
            {#each iceLevels as { value, title }}
              <option {value}>{title}</option>
            {/each}
          </select>
        </label>

        <label class="label-and-input">
          <input type="checkbox" bind:checked={$detailedScaleLocally} />Scale
          locally
        </label>

        <!-- {#if $detailedICELevel === 'cluster-lines'}
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:checked={showClusterDescriptions}
            />Describe clusters
          </label>
        {/if} -->
        <div class="context-container">
          <div>Context:</div>
          <label class="label-and-input">
            <input
              type="radio"
              bind:group={$detailedContextKind}
              name="context"
              value={'scatterplot'}
            />
            Scatterplot
          </label>
          {#if $detailedICELevel === 'cluster-lines'}
            <label class="label-and-input">
              <input
                type="radio"
                bind:group={$detailedContextKind}
                name="context"
                value={'cluster-descriptions'}
              />
              Cluster Descriptions
            </label>
          {/if}
          <label class="label-and-input">
            <input
              type="radio"
              bind:group={$detailedContextKind}
              name="context"
              value={'none'}
            />
            None
          </label>
        </div>
      {:else}
        <label class="label-and-input">
          <input type="checkbox" bind:checked={$detailedScaleLocally} />Scale
          locally
        </label>
        <button on:click={swapAxes} title="Swap x and y axes">Swap Axes</button>
      {/if}
    {/if}
  </div>
  <div class="zoomed-pdp-content" bind:this={div}>
    {#if pd === null}
      <div class="detailed-plot-message-container">
        <div class="detailed-plot-message-content">
          {#if $detailedFeature1 === '' && $detailedFeature2 === ''}
            <div style:text-align="center">
              Select one or two features above.
            </div>
          {:else}
            <div>
              The two-way PDP between {$detailedFeature1} and {$detailedFeature2}
              was not pre-computed, since we did not detect a likely interaction
              between the two features.
            </div>
            <button
              on:click={computeTwoWayPd}
              disabled={$two_way_to_calculate.length === 2}
              >{$two_way_to_calculate.length === 2
                ? 'Computing...'
                : 'Compute Now'}</button
            >
          {/if}
        </div>
      </div>
    {:else if pd.num_features === 1}
      <div class="one-way-pdp-grid">
        {#if $detailedICELevel === 'cluster-lines' && pd.ice.num_clusters === 1}
          <div class="pdpilot-no-clusters-message">
            This feature does not have any distinct clusters of ICE lines.
          </div>
        {:else}
          <div style:flex="1">
            <PDP
              {pd}
              width={$detailedContextKind === 'none' ? gridWidth : halfWidth}
              height={gridHeight}
              scaleLocally={$detailedScaleLocally}
              showMarginalDistribution={false}
              marginTop={10}
              marginalPlotHeight={0}
              iceLevel={$detailedICELevel}
              {indices}
              allowBrushing={true}
              showColorLegend={false}
              showTitle={$detailedContextKind !== 'none' &&
                $detailedICELevel === 'cluster-lines'}
            />
          </div>

          {#if $detailedContextKind === 'cluster-descriptions'}
            <div style:flex="1">
              <ClusterDescriptions
                on:filter={onFilterIndices}
                {pd}
                features={pd.ice.clusters[pd.ice.num_clusters]
                  .interacting_features}
              />
            </div>
          {:else if $detailedContextKind === 'scatterplot'}
            <div style:flex="1">
              <FeatureVsLabels
                {pd}
                width={halfWidth}
                height={gridHeight}
                showMarginalDistribution={true}
                marginTop={marginalPlotHeight + 3}
                marginRight={marginalPlotHeight + 3}
                {marginalPlotHeight}
              />
            </div>
          {/if}
        {/if}
      </div>
    {:else}
      <div class="two-way-pdp-grid interactions-predictions-scatter">
        <div style:grid-area="two-way-interaction">
          <PDP
            {pd}
            width={thirdWidth}
            height={gridHeight}
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
            height={gridHeight}
            scaleLocally={$detailedScaleLocally}
            showMarginalPdp={true}
            marginTop={marginalPlotHeight + 1}
            marginRight={marginalPlotHeight + 1}
            {marginalPlotHeight}
            iceLevel={$detailedICELevel}
            showColorLegend={true}
            colorLegendTitle="Predictions"
          />
        </div>

        <div style:grid-area="scatter">
          <FeatureVsFeature
            {pd}
            width={thirdWidth}
            height={gridHeight}
            showMarginalDistribution={true}
            marginTop={marginalPlotHeight + 3}
            marginRight={marginalPlotHeight + 3}
            {marginalPlotHeight}
            colorLegendTitle="Ground Truth"
          />
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .zoomed-pdp-container {
    width: 100%;
    height: 100%;

    display: flex;
    flex-direction: column;
  }

  .zoomed-pdp-header {
    height: 2em;
    display: flex;
    align-items: center;
    background-color: white;
    gap: 1.5em;
    padding-left: 0.5em;
    padding-right: 0.5em;
    border-bottom: 1px solid var(--gray-1);
  }

  /* .feature-selects contains the two labels and dropdowns.
   In the header, we want the width of the dropdowns to shrink
   so that the header stays on one line. The select menu is 3
   levels down from the header. */

  .feature-selects {
    /* don't grow and do shrink */
    flex: 0 1 auto;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 0.5em;
  }

  .feature-selects label {
    /* don't grow and do shrink */
    flex: 0 1 auto;
    display: flex;
    align-items: center;
    gap: 0.25em;
    min-width: 0;
  }

  .feature-selects label span {
    /* don't grow and don't shrink */
    flex: 0 0 auto;
  }

  .feature-selects label select {
    /* don't grow and do shrink */
    flex: 0 1 auto;
    min-width: 0;
    text-overflow: ellipsis;
  }

  .zoomed-pdp-content {
    flex: 1;
    padding: 0.5em;
    /* this is needed to allow scrolling in cluster descriptions */
    min-height: 0px;
  }

  .one-way-pdp-grid {
    display: flex;
    width: 100%;
    height: 100%;
  }

  .two-way-pdp-grid {
    display: grid;
    width: 100%;
    height: 100%;
  }

  .label-and-input {
    /* don't grow and don't shrink */
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .interactions-predictions-scatter {
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-areas: 'two-way-interaction two-way-pdp scatter';
  }

  .detailed-plot-message-container {
    height: 100%;
    width: 100%;

    align-items: center;
    justify-content: center;

    display: flex;
  }

  .detailed-plot-message-content {
    width: 40em;

    display: flex;
    flex-direction: column;

    justify-content: center;

    gap: 1em;
  }

  .detailed-plot-message-content > button {
    margin: auto;
  }

  .pdpilot-no-clusters-message {
    flex: 1;
    text-align: center;
    align-self: center;
  }

  .context-container {
    /* don't grow and don't shrink */
    flex: 0 0 auto;

    display: flex;
    align-items: center;
    gap: 0.5em;
  }

  .context-container > div:first-child {
  }
</style>
