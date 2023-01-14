<script lang="ts">
  import type { OneWayPD, TwoWayPD, ICELevel } from '../types';
  import { createEventDispatcher, onMount } from 'svelte';
  import {
    one_way_pds,
    two_way_pds,
    globalColorPdpExtent,
    feature_names,
  } from '../stores';
  import PDP from './PDP.svelte';
  import ParallelCoordinates from './vis/ice-clusters/ParallelCoordinates.svelte';
  import StackedBars from './vis/ice-clusters/StackedBars.svelte';
  import StripPlot from './vis/ice-clusters/StripPlot.svelte';
  import BoxPlot from './vis/ice-clusters/BoxPlot.svelte';
  import ViolinPlot from './vis/ice-clusters/ViolinPlot.svelte';

  export let pd: OneWayPD | TwoWayPD;

  // header

  $: feature1 = pd.x_feature;
  $: feature2 = pd.num_features === 2 ? pd.y_feature : '';

  let scaleLocally: boolean = false;
  let showTrendLine: boolean = false;
  let iceLevel: ICELevel = 'none';

  const levels: ICELevel[] = ['none', 'mean', 'band', 'line'];

  $: if (iceLevel !== 'none') {
    showTrendLine = false;
  }

  let clusterDescriptions:
    | 'none'
    | 'parallel'
    | 'bars'
    | 'strip'
    | 'box'
    | 'violin' = 'none';
  $: if (iceLevel !== 'band' && iceLevel !== 'line') {
    clusterDescriptions = 'none';
  }

  // one-way PDPs
  let xPdp: OneWayPD | null = null;
  let yPdp: OneWayPD | null = null;

  let showMarginalDistribution: boolean = false;
  let showOneWayChecked: boolean = false;
  let showOneWay: boolean = false;
  let showInteractionsChecked: boolean = false;
  let showInteractions: boolean = false;

  $: showOneWay =
    pd.num_features === 2 &&
    showOneWayChecked &&
    xPdp !== null &&
    yPdp !== null;
  $: showInteractions = pd.num_features === 2 && showInteractionsChecked;

  const dispatch = createEventDispatcher<{
    zoom: OneWayPD | TwoWayPD;
  }>();

  function onChangeFeature(
    event: { currentTarget: HTMLSelectElement },
    whichFeature: number
  ) {
    let f1: string = '';
    let f2: string = '';

    if (whichFeature === 1) {
      f1 = event.currentTarget.value;
      f2 = feature2;
    } else {
      f1 = feature1;
      f2 = event.currentTarget.value;
    }

    if (f1 === f2) {
      f2 = '';
    }

    if (f2 === '') {
      const pd = $one_way_pds.find((d) => d.x_feature === f1);

      if (pd) {
        dispatch('zoom', pd);
      }
    } else {
      const pd = $two_way_pds.find(
        (d) =>
          (d.x_feature === f1 && d.y_feature === f2) ||
          (d.x_feature === f2 && d.y_feature === f1)
      );

      if (pd) {
        dispatch('zoom', pd);
      }
    }
  }

  // sizes

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  $: halfWidth = gridWidth / 2;
  $: halfHeight = gridHeight / 2;

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

  $: if (pd.num_features === 2) {
    let found = 0;

    xPdp = null;
    yPdp = null;

    for (let other of $one_way_pds) {
      if (other.x_feature === pd.x_feature) {
        found++;
        xPdp = other;
      } else if (other.x_feature === pd.y_feature) {
        found++;
        yPdp = other;
      }

      if (found === 2) {
        break;
      }
    }
  }
</script>

<div class="zoomed-pdp-container">
  <div class="zoomed-pdp-header">
    <div class="feature-selects">
      <label>
        <span>Feat. 1</span>
        <select value={feature1} on:change={(e) => onChangeFeature(e, 1)}>
          {#each $feature_names as feature}
            <option value={feature}>{feature}</option>
          {/each}
        </select>
      </label>

      {#if $two_way_pds.length > 0}
        <label>
          <span>Feat. 2</span>
          <select
            class="feature-select"
            value={feature2}
            on:change={(e) => onChangeFeature(e, 2)}
          >
            <option value="" />
            {#each $feature_names as feature}
              <option value={feature}>{feature}</option>
            {/each}
          </select>
        </label>
      {/if}
    </div>

    <label class="label-and-input">
      <input type="checkbox" bind:checked={scaleLocally} />Scale locally
    </label>

    <label class="label-and-input">
      <input type="checkbox" bind:checked={showMarginalDistribution} />
      {pd.num_features === 1
        ? 'Marginal distribution'
        : 'Marginal distributions'}
    </label>

    {#if pd.num_features === 2}
      <label class="label-and-input">
        <input type="checkbox" bind:checked={showOneWayChecked} />One-way PDPs
      </label>

      <label class="label-and-input">
        <input
          type="checkbox"
          bind:checked={showInteractionsChecked}
        />Interaction
      </label>
    {:else}
      <label class="label-and-input">
        <span>ICE:</span>
        <select bind:value={iceLevel}>
          {#each levels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </label>

      {#if iceLevel === 'band' || iceLevel === 'line'}
        <label class="label-and-input">
          <span>Descriptions:</span>
          <select bind:value={clusterDescriptions}>
            <option value="none">None</option>
            <option value="bars">Histograms</option>
            <option value="box">Box Plot</option>
            <option value="violin">Violin Plot</option>
            <option value="parallel">Parallel Coordinates</option>
            <option value="strip">Strip Plot</option>
          </select>
        </label>
      {/if}

      {#if pd.ordered && iceLevel === 'none'}
        <label class="label-and-input">
          <input type="checkbox" bind:checked={showTrendLine} />Trend line
        </label>
      {/if}
    {/if}
  </div>
  <div class="zoomed-pdp-content" bind:this={div}>
    {#if pd.num_features === 1}
      <div class="one-way-pdp-grid">
        <div style:flex="1">
          <PDP
            {pd}
            globalColor={$globalColorPdpExtent}
            width={clusterDescriptions !== 'none' ? halfWidth : gridWidth}
            height={gridHeight}
            {scaleLocally}
            {showTrendLine}
            {showMarginalDistribution}
            {iceLevel}
            showColorLegend={false}
          />
        </div>

        {#if clusterDescriptions === 'parallel'}
          <div style:flex="1">
            <ParallelCoordinates
              {pd}
              width={halfWidth}
              height={gridHeight}
              features={pd.ice.interacting_features}
            />
          </div>
        {:else if clusterDescriptions === 'bars'}
          <div style:flex="1">
            <StackedBars
              {pd}
              width={halfWidth}
              height={gridHeight}
              features={pd.ice.interacting_features}
            />
          </div>
        {:else if clusterDescriptions === 'strip'}
          <div style:flex="1">
            <StripPlot
              {pd}
              width={halfWidth}
              height={gridHeight}
              features={pd.ice.interacting_features}
            />
          </div>
        {:else if clusterDescriptions === 'box'}
          <div style:flex="1">
            <BoxPlot
              {pd}
              width={halfWidth}
              height={gridHeight}
              features={pd.ice.interacting_features}
            />
          </div>
        {:else if clusterDescriptions === 'violin'}
          <div style:flex="1">
            <ViolinPlot
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
        class="two-way-pdp-grid showOneWay-{showOneWay}-showInteraction-{showInteractions}"
      >
        {#if xPdp !== null && yPdp !== null && showOneWay}
          <div style:grid-area="one-way-left">
            <PDP
              pd={xPdp}
              globalColor={$globalColorPdpExtent}
              width={halfWidth}
              height={halfHeight}
              {scaleLocally}
              showTrendLine={false}
              {showMarginalDistribution}
              iceLevel="none"
            />
          </div>

          <div style:grid-area="one-way-right">
            <PDP
              pd={yPdp}
              globalColor={$globalColorPdpExtent}
              width={halfWidth}
              height={halfHeight}
              {scaleLocally}
              showTrendLine={false}
              {showMarginalDistribution}
              iceLevel="none"
            />
          </div>
        {/if}

        <div style:grid-area="main">
          <PDP
            {pd}
            globalColor={$globalColorPdpExtent}
            width={showOneWay && showInteractions ? halfWidth : gridWidth}
            height={showOneWay || showInteractions ? halfHeight : gridHeight}
            {scaleLocally}
            {showTrendLine}
            {showMarginalDistribution}
            {iceLevel}
            showColorLegend={true}
          />
        </div>

        {#if showInteractions && pd.num_features === 2}
          <div style:grid-area="interaction">
            <PDP
              {pd}
              globalColor={$globalColorPdpExtent}
              width={showOneWay ? halfWidth : gridWidth}
              height={halfHeight}
              {scaleLocally}
              {showTrendLine}
              {showMarginalDistribution}
              iceLevel="none"
              showInteractions={true}
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
    border-top: 1px solid var(--gray-1);
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

  .showOneWay-true-showInteraction-true {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'main interaction';
  }

  .showOneWay-true-showInteraction-false {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'main main';
  }

  .showOneWay-false-showInteraction-true {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'main main'
      'interaction interaction';
  }

  .showOneWay-false-showInteraction-false {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'main main'
      'main main';
  }
</style>
