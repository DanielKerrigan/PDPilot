<script lang="ts">
  import type { OneWayPD, TwoWayPD, PDSortingOption, ICELevel } from '../types';
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
    highlighted_indices,
    brushingInProgress,
    highlightedDistributions,
    feature_info,
    detailedShowDistributions,
    detailedScaleLocally,
    detailedICELevel,
  } from '../stores';
  import InfoTooltip from './InfoTooltip.svelte';

  export let data: OneWayPD[] | TwoWayPD[];
  export let sortingOptions: PDSortingOption[];
  export let noPlotsMessage: string;

  $: ways = isOneWayPdArray(data) ? 1 : 2;

  let sortedData: OneWayPD[] | TwoWayPD[];

  const iceLevels: { value: ICELevel; title: string }[] = [
    { value: 'lines', title: 'Standard' },
    { value: 'centered-lines', title: 'Centered' },
    { value: 'cluster-centers', title: 'Clusters' },
  ];

  let iceLevel: ICELevel = 'lines';

  let colorShows: 'predictions' | 'interactions' = 'interactions';
  let showMarginalDistribution = false;

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

  function getNumberOfRowsAndCols(perPage: number) {
    const numRows = Math.ceil(Math.sqrt(perPage));
    const numCols = Math.ceil(perPage / numRows);

    if (ways === 1) {
      return [numRows, numCols];
    } else {
      return [numCols, numRows];
    }
  }

  $: perPage = Math.min(data.length, 12);

  $: [numRows, numCols] = getNumberOfRowsAndCols(perPage);

  $: pdpWidth = Math.floor(gridWidth / numCols);
  $: pdpHeight = Math.floor(gridHeight / numRows);

  // brushing

  let brushingSinceSorting = false;

  // header

  const legendHeight = 24;
  let legendWidth = 140;

  // sorting

  let sortingOption = sortingOptions[0];

  $: if (!sortingOption.forBrushing) {
    sortedData = sortingOption.sort(data);
    // when the sorting or data changes, go to the first page
    setPage(1);
  }

  // show marginal distributions when highlighted distribution metric is chosen.
  // this is in separate function so that the reactive if statement doesn't run
  // when showMarginalDistribution is updated.
  function setShowDistributionToTrue() {
    showMarginalDistribution = true;
  }

  $: if (sortingOption.name === 'Highlighted distribution') {
    setShowDistributionToTrue();
  }

  // we don't want changes to highlights to trigger this
  function sortByBrushing(data: OneWayPD[] | TwoWayPD[]) {
    brushingSinceSorting = false;

    sortedData = sortingOption.sort(data, {
      highlightedIndices: $highlighted_indices,
      highlightedDistributions: $highlightedDistributions,
      featureInfo: $feature_info,
    });

    // when the sorting or data changes, go to the first page
    setPage(1);
  }
  $: if (sortingOption.forBrushing) {
    sortByBrushing(data);
  }

  $: if ($brushingInProgress) {
    brushingSinceSorting = true;
  }

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

  // scaling

  let scaleLocally = false;

  // selecting pdp

  function onClickPdp(pd: OneWayPD | TwoWayPD) {
    $detailedFeature1 = pd.x_feature;
    $detailedFeature2 = pd.num_features === 2 ? pd.y_feature : '';

    $detailedShowDistributions = showMarginalDistribution;
    $detailedScaleLocally = scaleLocally;

    if (pd.num_features === 1) {
      $detailedICELevel =
        iceLevel === 'cluster-centers' ? 'cluster-lines' : iceLevel;
    }

    $selectedTab = 'detailed-plot';
  }
</script>

<div class="group-container">
  <div class="group-header">
    <div class="page-change dont-shrink">
      <button
        disabled={currentPage <= 1}
        on:click={() => setPage(currentPage - 1)}
        title="Previous page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="pdpilot-icon icon-tabler icon-tabler-arrow-left"
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
        title="Next page"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="pdpilot-icon icon-tabler icon-tabler-arrow-right"
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

    <div class="dont-shrink label-and-input">
      <label class="label-and-input">
        Sort
        <select bind:value={sortingOption}>
          {#each sortingOptions as option}
            <option value={option}>{option.name}</option>
          {/each}
        </select>
      </label>

      <InfoTooltip
        kind="help"
        left="0"
        top="0"
        marginRight="1em"
        marginTop="1.5em"
        width="30em"
      >
        <div>
          {#if ways === 1}
            <ul>
              <li>
                <span class="pdpilot-bold">Variance:</span> Plots that have more
                variance in their ICE lines are ranked higher.
              </li>
              <li>
                <span class="pdpilot-bold">Cluster difference:</span> Plots that
                have ICE clusters farther from the partial dependence line are ranked
                higher.
              </li>
              <li>
                <span class="pdpilot-bold">Highlighted similarity:</span> Plots where
                the highlighted lines are closer together and farther from the partial
                dependence line are ranked higher.
              </li>
              <li>
                <span class="pdpilot-bold">Highlighted distribution:</span> Plots
                for features whose distributions of highlighted instances are more
                different from the overall distributions are ranked higher.
              </li>
            </ul>
          {:else}
            <ul>
              <li>
                <span class="pdpilot-bold">Interaction:</span> Plots for feature
                pairs with more interaction are ranked higher.
              </li>
              <li>
                <span class="pdpilot-bold">Variance:</span> Plots that have more
                variation in their average predictions are ranked higher.
              </li>
            </ul>
          {/if}
        </div>
      </InfoTooltip>
    </div>

    {#if ways === 1 && sortingOption.forBrushing}
      <button
        title="Update sorting"
        disabled={!brushingSinceSorting}
        on:click={() => sortByBrushing(data)}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="pdpilot-icon icon-tabler icon-tabler-refresh"
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
          <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4" />
          <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" />
        </svg>
      </button>
    {/if}

    {#if ways === 1}
      <label class="label-and-input dont-shrink">
        Plot
        <select bind:value={iceLevel}>
          {#each iceLevels as { value, title }}
            <option {value}>{title}</option>
          {/each}
        </select>
      </label>
    {/if}

    <label class="label-and-input dont-shrink">
      <input type="checkbox" bind:checked={scaleLocally} /><span
        >Scale locally</span
      >
    </label>

    {#if ways === 1}
      <label class="label-and-input">
        <input type="checkbox" bind:checked={showMarginalDistribution} /><span
          >Distributions</span
        >
      </label>
    {/if}

    <div class="two-way-color-container">
      {#if ways === 2}
        <div class="label-and-input dont-shrink">
          <label class="label-and-input">
            Color
            <select bind:value={colorShows}>
              <option value="interactions">interactions</option>
              <option value="predictions">predictions</option>
            </select>
          </label>

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
                between the pair of features. It indicates whether the
                interaction between the two features makes the model's average
                prediction for the given values <span
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
        </div>
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
    {#if pageCharts.length === 0}
      <div class="pdpilot-no-plots-container">
        <div class="pdpilot-no-plots-message">
          {noPlotsMessage}
        </div>
      </div>
    {:else}
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
              {showMarginalDistribution}
              marginTop={ways === 1 ? 11 : 5}
              marginRight={10}
              distributionHeight={ways === 1 ? 10 : 0}
              showColorLegend={scaleLocally}
              {iceLevel}
              allowBrushing={ways === 1}
              showBrushedBorder={ways === 1}
              iceLineWidth={0.5}
            />
            <button class="expand-pdp-button" on:click={() => onClickPdp(pd)}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="pdpilot-icon icon-tabler icon-tabler-arrows-maximize"
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
    {/if}
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
    padding: 1px;
  }

  .pdpilot-no-plots-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pdpilot-no-plots-message {
    max-width: 28em;
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

  ul {
    list-style: none;
  }

  li + li {
    margin-top: 0.5em;
  }
</style>
