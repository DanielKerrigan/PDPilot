<script lang="ts">
  import type { DoublePDPData, SinglePDPData, PDSortingOption } from '../types';
  import PDP from './PDP.svelte';
  import QuantitativeColorLegend from './vis/two_way/QuantitativeColorLegend.svelte';
  import { onMount, createEventDispatcher } from 'svelte';
  import { globalColorPdpExtent } from '../stores';

  export let title: string;
  export let data: SinglePDPData[] | DoublePDPData[];
  export let showColorLegend: boolean = false;
  export let showShowTrendLine: boolean = false;
  export let showShowIceClusters: boolean = false;
  export let sortingOptions: PDSortingOption[];

  let showIceClusters: boolean = false;

  let div: HTMLDivElement;
  let legendDiv: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  let pdpWidth: number;
  let pdpHeight: number;

  let expanded = true;

  let showTrendLine: boolean = false;

  $: if (showIceClusters) {
    showTrendLine = false;
  }

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

  // expand and collapse

  function toggle() {
    expanded = !expanded;
  }

  // number of rows and columns

  $: perPage = Math.min(data.length, 6);
  // TODO: https://stackoverflow.com/questions/60104268/default-panel-layout-of-ggplot2facet-wrap
  $: numRows = Math.floor(Math.sqrt(perPage));
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

  function onKeyDownPageChange(ev: KeyboardEvent) {
    if (ev.key === 'ArrowLeft') {
      setPage(currentPage - 1);
    } else if (ev.key === 'ArrowRight') {
      setPage(currentPage + 1);
    }
  }

  // scaling

  let scaleLocally = false;

  // selecting pdp

  const dispatchZoom = createEventDispatcher<{
    zoom: SinglePDPData | DoublePDPData;
  }>();

  function onClickPdp(pd: SinglePDPData | DoublePDPData) {
    dispatchZoom('zoom', pd);
  }

  function onKeyDownPdp(ev: KeyboardEvent, pd: SinglePDPData | DoublePDPData) {
    if (ev.key === 'Enter' || ev.key === ' ') {
      onClickPdp(pd);
    }
  }
</script>

<div class="group-container" class:hide-plots={!expanded}>
  <div class="group-header">
    <div class="toggle-and-title dont-shrink">
      <button class="toggle-button" on:click={toggle}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="icon icon-tabler icon-tabler-chevron-down"
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
          <polyline points={'6 9 12 15 18 9'} class:rotate={!expanded} />
        </svg>
      </button>

      <div class="group-title">{title}</div>
    </div>

    {#if expanded && data.length > 0}
      <div
        class="page-change dont-shrink"
        on:keydown={onKeyDownPageChange}
        tabindex="0"
      >
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
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
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

      <label class="dont-shrink">
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

      {#if showShowTrendLine && !showIceClusters}
        <label class="label-and-input dont-shrink">
          <input type="checkbox" bind:checked={showTrendLine} /><span
            >Show trend line</span
          >
        </label>
      {/if}

      {#if showShowIceClusters}
        <label class="label-and-input">
          <input type="checkbox" bind:checked={showIceClusters} /><span
            >Centered ICE Clusters</span
          >
        </label>
      {/if}
    {/if}
    <!--
      The legend is outside the above if statement because we want this div
      to persist so that the ResizeObserver works correctly.
    -->
    <div
      class="legend-container"
      class:dont-show={!expanded ||
        data.length == 0 ||
        !showColorLegend ||
        scaleLocally}
    >
      <div class="legend-title">Prediction</div>
      <div class="legend" bind:this={legendDiv}>
        <QuantitativeColorLegend
          width={legendWidth}
          height={legendHeight}
          color={$globalColorPdpExtent}
          marginLeft={15}
          marginRight={15}
        />
      </div>
    </div>
  </div>

  <div class="pdp-grid-container" bind:this={div}>
    {#if expanded}
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
        {#each pageCharts as pdp (pdp.id)}
          <div
            on:click={() => onClickPdp(pdp)}
            tabindex="0"
            on:keydown={(e) => onKeyDownPdp(e, pdp)}
            class="pdp-grid-element"
            style:cursor="pointer"
            style:max-width="{pdpWidth}px"
            style:max-height="{pdpHeight}px"
          >
            <PDP
              {pdp}
              globalColor={$globalColorPdpExtent}
              width={pdpWidth}
              height={pdpHeight}
              {scaleLocally}
              {showTrendLine}
              showMarginalDistribution={false}
              showColorLegend={scaleLocally}
              iceLevel={showIceClusters ? 'mean' : 'none'}
            />
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  /* https://stackoverflow.com/a/69029387/5016634 */
  .icon-tabler-chevron-down {
    -webkit-transform: translate(0px, 0px);
    transform: translate(0px, 0px);
  }

  .group-container {
    flex: 1;

    display: flex;
    flex-direction: column;

    min-height: 2em;
  }

  .group-title {
    width: 8ch;
  }

  .toggle-and-title {
    display: flex;
    align-items: center;
    gap: 0.5em;
  }

  .hide-plots {
    flex: 0;
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
    border-top: 1px solid var(--gray-1);
    border-bottom: 1px solid var(--gray-1);
    padding-left: 0.5em;
    padding-right: 0.5em;
  }

  .legend-container {
    flex: 1;
    margin-left: auto;

    display: flex;
    align-items: center;
  }

  .legend {
    flex: 1;
  }

  .page-change {
    display: flex;
    align-items: center;
  }

  /* this outlines the page change area when the user clicks there */
  .page-change:focus {
    outline: var(--blue) auto 1px;
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

  .icon-tabler-chevron-down polyline {
    transition: transform 200ms;
    transform-origin: 50% 50%;
  }

  .pdp-grid-element {
    cursor: pointer;
  }

  .pdp-grid-element:hover {
    outline: var(--blue) auto 1px;
  }

  .rotate {
    transform: rotate(-90deg);
  }

  .dont-shrink {
    flex: 0 0 auto;
  }

  .dont-show {
    display: none;
  }
</style>
