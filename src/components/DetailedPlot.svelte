<script lang="ts">
  import type { OneWayPD, ICELevel, TwoWayPD } from '../types';
  import { onMount } from 'svelte';
  import {
    two_way_pds,
    feature_names,
    two_way_to_calculate,
    detailedFeature1,
    detailedFeature2,
    featureToPd,
  } from '../stores';
  import PDP from './PDP.svelte';
  import ViolinPlot from './vis/ice-clusters/ViolinPlot.svelte';

  let pd: OneWayPD | TwoWayPD | null = null;

  let scaleLocally = false;

  const marginalChartHeight = 50;

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

  let xPdp: OneWayPD | null = null;
  let yPdp: OneWayPD | null = null;

  $: if (pd && pd.num_features === 2) {
    xPdp = $featureToPd.get(pd.x_feature) ?? null;
    yPdp = $featureToPd.get(pd.y_feature) ?? null;
  }

  let showClusterDescriptions = false;

  const iceLevels: { value: ICELevel; title: string }[] = [
    { value: 'lines', title: 'Standard' },
    { value: 'centered-lines', title: 'Centered' },
    { value: 'cluster-lines', title: 'Clusters' },
  ];

  let iceLevel: ICELevel = 'lines';

  $: if (iceLevel !== 'cluster-lines') {
    showClusterDescriptions = false;
  }

  let showMarginalDistribution = false;
  let showOneWay = true;
  let colorShows: 'both' | 'interactions' | 'predictions' = 'both';

  // sizes

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  $: halfWidth = gridWidth / 2;
  // $: halfHeight = gridHeight / 2;

  $: thirdHeight = gridHeight / 3;
  $: twoThirdHeight = (2 * gridHeight) / 3;

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

  $: if (!showClusterDescriptions) {
    indices = null;
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
      <label class="label-and-input">
        <input type="checkbox" bind:checked={showMarginalDistribution} />
        {pd.num_features === 1 ? 'Distribution' : 'Distributions'}
      </label>

      <label class="label-and-input">
        <input type="checkbox" bind:checked={scaleLocally} />Scale locally
      </label>

      {#if pd.num_features === 2}
        <label class="label-and-input">
          <input type="checkbox" bind:checked={showOneWay} />One-way plots
        </label>

        <label class="label-and-input">
          Color
          <select bind:value={colorShows}>
            <option value="both">both</option>
            <option value="interactions">interactions</option>
            <option value="predictions">predictions</option>
          </select>
        </label>
      {:else}
        <label class="label-and-input">
          ICE:
          <select bind:value={iceLevel}>
            {#each iceLevels as { value, title }}
              <option {value}>{title}</option>
            {/each}
          </select>
        </label>
        {#if iceLevel === 'cluster-lines'}
          <label class="label-and-input">
            <input
              type="checkbox"
              bind:checked={showClusterDescriptions}
            />Describe clusters
          </label>
        {/if}
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
        <div style:flex="1">
          <PDP
            {pd}
            width={showClusterDescriptions ? halfWidth : gridWidth}
            height={gridHeight}
            {scaleLocally}
            {showMarginalDistribution}
            marginTop={showMarginalDistribution ? marginalChartHeight : 10}
            distributionHeight={showMarginalDistribution
              ? marginalChartHeight
              : 0}
            {iceLevel}
            {indices}
            showColorLegend={false}
          />
        </div>

        {#if showClusterDescriptions}
          <div style:flex="1">
            <ViolinPlot
              on:filter={onFilterIndices}
              {pd}
              width={halfWidth}
              height={gridHeight}
              features={pd.ice.interacting_features}
            />
          </div>
        {/if}
      </div>
    {:else}
      <div
        class="two-way-pdp-grid showOneWay-{xPdp !== null &&
          yPdp !== null &&
          showOneWay}-color-{colorShows}"
      >
        {#if xPdp !== null && yPdp !== null && showOneWay}
          <div style:grid-area="one-way-left">
            <PDP
              pd={xPdp}
              width={halfWidth}
              height={thirdHeight}
              {scaleLocally}
              {showMarginalDistribution}
              marginTop={showMarginalDistribution ? marginalChartHeight : 10}
              distributionHeight={showMarginalDistribution
                ? marginalChartHeight
                : 0}
              iceLevel="lines"
            />
          </div>

          <div style:grid-area="one-way-right">
            <PDP
              pd={yPdp}
              width={halfWidth}
              height={thirdHeight}
              {scaleLocally}
              {showMarginalDistribution}
              marginTop={showMarginalDistribution ? marginalChartHeight : 10}
              distributionHeight={showMarginalDistribution
                ? marginalChartHeight
                : 0}
              iceLevel="lines"
            />
          </div>
        {/if}

        {#if colorShows === 'both' || colorShows === 'interactions'}
          <div style:grid-area="two-way-interaction">
            <PDP
              {pd}
              width={colorShows === 'both' ? halfWidth : gridWidth}
              height={xPdp !== null && yPdp !== null && showOneWay
                ? twoThirdHeight
                : gridHeight}
              {scaleLocally}
              {showMarginalDistribution}
              marginTop={showMarginalDistribution ? marginalChartHeight : 10}
              marginRight={showMarginalDistribution ? marginalChartHeight : 10}
              distributionHeight={showMarginalDistribution
                ? marginalChartHeight
                : 0}
              iceLevel="lines"
              colorShows="interactions"
              showColorLegend={true}
            />
          </div>
        {/if}

        {#if colorShows === 'both' || colorShows === 'predictions'}
          <div style:grid-area="two-way-pdp">
            <PDP
              {pd}
              width={colorShows === 'both' ? halfWidth : gridWidth}
              height={xPdp !== null && yPdp !== null && showOneWay
                ? twoThirdHeight
                : gridHeight}
              {scaleLocally}
              {showMarginalDistribution}
              marginTop={showMarginalDistribution ? marginalChartHeight : 10}
              marginRight={showMarginalDistribution ? marginalChartHeight : 10}
              distributionHeight={showMarginalDistribution
                ? marginalChartHeight
                : 0}
              {iceLevel}
              showColorLegend={true}
            />
          </div>
        {/if}
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

  .showOneWay-true-color-both {
    grid-template-rows: 1fr 2fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'two-way-interaction two-way-pdp';
  }

  .showOneWay-true-color-interactions {
    grid-template-rows: 1fr 2fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'two-way-interaction two-way-interaction';
  }

  .showOneWay-true-color-predictions {
    grid-template-rows: 1fr 2fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'two-way-pdp two-way-pdp';
  }

  .showOneWay-false-color-both {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'two-way-interaction two-way-pdp'
      'two-way-interaction two-way-pdp';
  }

  .showOneWay-false-color-interactions {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'two-way-interaction two-way-interaction'
      'two-way-interaction two-way-interaction';
  }

  .showOneWay-false-color-predictions {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'two-way-pdp two-way-pdp'
      'two-way-pdp two-way-pdp';
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
</style>
