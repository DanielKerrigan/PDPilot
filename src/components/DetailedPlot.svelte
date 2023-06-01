<script lang="ts">
  import type { OneWayPD, TwoWayPD } from '../types';
  import {
    two_way_pds,
    feature_names,
    two_way_to_calculate,
    detailedFeature1,
    detailedFeature2,
    detailedScaleLocally,
    featureToPd,
    feature_info,
  } from '../stores';
  import OneWayDetailedPlot from './OneWayDetailedPlot.svelte';
  import TwoWayDetailedPlot from './TwoWayDetailedPlot.svelte';

  let pd: OneWayPD | TwoWayPD | null = null;

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

  $: $detailedFeature1, $detailedFeature2, $featureToPd, onChangeFeature();

  $: if ($two_way_pds) {
    getComputedTwoWayPd();
  }

  $: xFeatureInfo = pd ? $feature_info[pd.x_feature] : null;
  $: yFeatureInfo =
    pd && pd.num_features === 2 ? $feature_info[pd.y_feature] : null;

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
        <span>Feature 1</span>
        <select bind:value={$detailedFeature1}>
          <option value="" />
          {#each $feature_names as feature}
            <option value={feature}>{feature}</option>
          {/each}
        </select>
      </label>

      <label>
        <span>Feature 2</span>
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
        <input type="checkbox" bind:checked={$detailedScaleLocally} />Scale
        locally
      </label>
      {#if pd.num_features === 2}
        <button on:click={swapAxes} title="Swap x and y axes">Swap Axes</button>
      {/if}
    {/if}
  </div>
  <div class="zoomed-pdp-content">
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
    {:else if pd.num_features === 1 && xFeatureInfo}
      <OneWayDetailedPlot {pd} featureInfo={xFeatureInfo} />
    {:else if pd.num_features === 2 && xFeatureInfo && yFeatureInfo}
      <TwoWayDetailedPlot {pd} {xFeatureInfo} {yFeatureInfo} />
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

  .label-and-input {
    /* don't grow and don't shrink */
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    gap: 0.25em;
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
