<script lang="ts">
  import type { OneWayPD, TwoWayPD, PDSortingOption } from '../types';
  import { isOneWayPdArray } from '../types';
  import PDP from './PDP.svelte';
  import QuantitativeColorLegend from './vis/two-way/QuantitativeColorLegend.svelte';
  import { onMount } from 'svelte';
  import {
    globalColorTwoWayPdp,
    globalColorTwoWayInteraction,
    detailedFeature1,
    detailedFeature2,
    selectedTab,
  } from '../stores';
  import InfoTooltip from './InfoTooltip.svelte';

  export let data: OneWayPD[] | TwoWayPD[];
  export let sortingOptions: PDSortingOption[];

  $: ways = isOneWayPdArray(data) ? 1 : 2;

  let showIceClusters = false;
  let colorShows: 'predictions' | 'interactions' = 'interactions';

  let div: HTMLDivElement;
  let legendDiv: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  let pdpWidth: number;
  let pdpHeight: number;

  onMount(() => {
    // Adapted from https://blog.sethcorker.com/question/how-do-you-use-the-resize-observer-api-in-svelte/
    // and https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver
    const gridResizeObserver = new ResizeObserver(
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

    gridResizeObserver.observe(div);

    const legendResizeObserver = new ResizeObserver(
      (entries: ResizeObserverEntry[]) => {
        if (entries.length !== 1) {
          return;
        }

        const entry: ResizeObserverEntry = entries[0];

        if (entry.contentBoxSize) {
          const contentBoxSize = Array.isArray(entry.contentBoxSize)
            ? entry.contentBoxSize[0]
            : entry.contentBoxSize;

          legendWidth = contentBoxSize.inlineSize;
        } else {
          legendWidth = entry.contentRect.width;
        }
      }
    );

    legendResizeObserver.observe(legendDiv);

    return () => {
      gridResizeObserver.unobserve(div);
      legendResizeObserver.unobserve(div);
    };
  });

  // number of rows and columns

  $: perPage = Math.min(data.length, 12);
  $: numRows = Math.ceil(Math.sqrt(perPage));
  $: numCols = Math.ceil(perPage / numRows);

  $: pdpWidth = Math.floor(gridWidth / numCols);
  $: pdpHeight = Math.floor(gridHeight / numRows);

  // header

  const legendHeight = 24;
  let legendWidth = 140;

  // sorting

  let sortingOption = sortingOptions[0];

  $: sortedData = sortingOption.sort(data);

  // pagination

  let currentPage = 1;

  $: numPages = Math.ceil(data.length / perPage);

  $: pageCharts = sortedData.slice(
    (currentPage - 1) * perPage,
    currentPage * perPage
  );

  function setPage(page: number) {
    if (page < 1 || page > numPages) {
      return;
    }

    currentPage = page;
  }

  $: data, setPage(1);

  // scaling

  let scaleLocally = false;

  // selecting pdp

  function onClickPdp(pd: OneWayPD | TwoWayPD) {
    $detailedFeature1 = pd.x_feature;
    $detailedFeature2 = pd.num_features === 2 ? pd.y_feature : '';
    $selectedTab = 'detailed-plot';
  }
</script>

<div class="group-container">
  <div class="group-header">
    <div class="page-change dont-shrink">
      <button
        disabled={currentPage <= 1}
        on:click={() => setPage(currentPage - 1)}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="icon icon-tabler icon-tabler-arrow-left"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path stroke="none" d=" M0 0h24v24H0z" fill="none" />
          <line x1="5" y1="12" x2="19" y2="12" />
          <line x1="5" y1="12" x2="11" y2="18" />
          <line x1="5" y1="12" x2="11" y2="6" />
        </svg>
      </button>

      <div class="current-page-number">{currentPage}</div>

      <button
        disabled={currentPage >= numPages}
        on:click={() => setPage(currentPage + 1)}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="icon icon-tabler icon-tabler-arrow-right"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <line x1="5" y1="12" x2="19" y2="12" />
          <line x1="13" y1="18" x2="19" y2="12" />
          <line x1="13" y1="6" x2="19" y2="12" />
        </svg>
      </button>
    </div>

    <label class="label-and-input dont-shrink">
      Sort by
      <select bind:value={sortingOption}>
        {#each sortingOptions as option}
          <option value={option}>{option.name}</option>
        {/each}
      </select>
    </label>

    <label class="label-and-input dont-shrink">
      <input type="checkbox" bind:checked={scaleLocally} /><span
        >Scale locally</span
      >
    </label>

    {#if ways === 1}
      <label class="label-and-input">
        <input type="checkbox" bind:checked={showIceClusters} /><span
          >Cluster ICE lines</span
        >
      </label>
    {/if}

    <div class="two-way-color-container">
      {#if ways === 2}
        <label class="label-and-input dont-shrink">
          Color
          <select bind:value={colorShows}>
            <option value="interactions">interactions</option>
            <option value="predictions">predictions</option>
          </select>
        </label>
      {/if}
      <!--
      We want this div to persist so that the ResizeObserver works correctly.
      -->
      <div
        class="two-way-color-legend"
        class:dont-show={ways === 1 || scaleLocally}
        bind:this={legendDiv}
      >
        <QuantitativeColorLegend
          width={legendWidth}
          height={legendHeight}
          color={colorShows === 'interactions'
            ? $globalColorTwoWayInteraction
            : $globalColorTwoWayPdp}
          marginLeft={15}
          marginRight={15}
        />
      </div>
      {#if ways === 2}
        <InfoTooltip
          kind="help"
          right="0"
          top="0"
          marginRight="1em"
          marginTop="1.5em"
          width="30em"
        >
          <div>
            {#if colorShows === 'interactions'}
              This color scale shows the difference between the value in a
              two-way PDP and the expected value if there was no interaction
              between the pair of features. It indicates whether the interaction
              between the two features makes the model's average prediction for
              the given values <span
                style:background={$globalColorTwoWayInteraction.interpolator()(
                  0.1
                )}
                style:border-radius="4px"
                style:padding="0.125em 0.25em"
                style:color="white">lower</span
              >
              or
              <span
                style:background={$globalColorTwoWayInteraction.interpolator()(
                  0.9
                )}
                style:border-radius="4px"
                style:padding="0.125em 0.25em"
                style:color="white">higher</span
              >. The units are the same as your target variable.
            {:else}
              This color scale is for a standard two-way PDP. The color of a
              cell represents the model's average prediction when setting the
              instances to have the given values for pair of features.
            {/if}
          </div>
        </InfoTooltip>
      {/if}
    </div>
  </div>

  <div class="pdp-grid-container" bind:this={div}>
    <!--
        Using repeat({numCols}, minmax(0,{pdpWidth}px)) was causing the charts to infinitely
        expand when selecting "Scale locally" in Jupyter Lab.
        This would happen even when replacing the PDP component with a div.

        I don't exactly know why this was happening or why it was only in Jupyter Lab. It may be related
        to the below links.

        https://css-tricks.com/preventing-a-grid-blowout/
        https://stackoverflow.com/questions/43311943/prevent-content-from-expanding-grid-items
        https://stackoverflow.com/questions/52861086/why-does-minmax0-1fr-work-for-long-elements-while-1fr-doesnt
       -->
    <div
      class="pdp-grid"
      style:grid-template-columns="repeat({numCols}, minmax(0,{pdpWidth}px))"
      style:grid-template-rows="repeat({numRows}, minmax(0,{pdpHeight}px))"
    >
      {#each pageCharts as pd (pd.id)}
        <div
          class="pdp-grid-element"
          style:max-width="{pdpWidth}px"
          style:max-height="{pdpHeight}px"
        >
          <PDP
            {pd}
            width={pdpWidth}
            height={pdpHeight}
            {scaleLocally}
            {colorShows}
            marginalDistributionKind={'none'}
            marginTop={10}
            marginRight={10}
            showColorLegend={scaleLocally}
            iceLevel={showIceClusters ? 'cluster-centers' : 'lines'}
          />
          <button class="expand-pdp-button" on:click={() => onClickPdp(pd)}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="icon icon-tabler icon-tabler-arrows-maximize"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              stroke-width="2"
              stroke="currentColor"
              fill="none"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path
                d="M16 4l4 0l0 4m-6 2l6 -6m-12 16l-4 0l0 -4m0 4l6 -6m6 6l4 0l0 -4m-6 -2l6 6m-12 -16l-4 0l0 4m0 -4l6 6"
              />
            </svg>
          </button>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .group-container {
    height: 100%;
    width: 100%;

    display: flex;
    flex-direction: column;

    min-height: 2em;
  }

  .pdp-grid-container {
    flex: 1;
    min-height: 0;
  }

  .pdp-grid {
    height: 100%;
    display: grid;
  }

  .group-header {
    height: 2em;
    display: flex;
    align-items: center;
    gap: 1em;
    border-bottom: 1px solid var(--gray-1);
    padding-left: 0.5em;
    padding-right: 0.5em;
  }

  .two-way-color-container {
    flex: 1;
    margin-left: auto;

    display: flex;
    align-items: center;
  }

  .two-way-color-legend {
    flex: 1;
  }

  .page-change {
    display: flex;
    align-items: center;
  }

  .current-page-number {
    width: 2em;
    text-align: center;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .pdp-grid-element {
    position: relative;
  }

  /* https://stackoverflow.com/a/40891870 */
  .pdp-grid-element:hover .expand-pdp-button {
    display: block;
  }

  .expand-pdp-button {
    position: absolute;
    display: none;
    bottom: 2px;
    left: 2px;
  }

  .dont-shrink {
    flex: 0 0 auto;
  }

  .dont-show {
    display: none;
  }
</style>
