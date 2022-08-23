<script lang="ts">
  import type { DoublePDPData, SinglePDPData, PDSortingOption } from '../types';
  import PDPContainer from './PDPContainer.svelte';
  import { scaleSequential } from 'd3-scale';
  import { interpolateYlGnBu } from 'd3-scale-chromatic';
  import QuantitativeColorLegend from './vis/two_way/QuantitativeColorLegend.svelte';
  import { onMount } from 'svelte';
  import { nice_prediction_extent } from '../stores';

  export let title: string;
  export let data: SinglePDPData[] | DoublePDPData[];
  export let showColorLegend: boolean = false;
  export let sortingOptions: PDSortingOption[];

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  let pdpWidth: number;
  let pdpHeight: number;

  let expanded = true;

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

  // expand and collapse

  function toggle() {
    expanded = !expanded;
  }

  // number of rows and columns

  $: perPage = Math.min(data.length, 6);
  // TODO: https://stackoverflow.com/questions/60104268/default-panel-layout-of-ggplot2facet-wrap
  $: numRows = Math.floor(Math.sqrt(perPage));
  $: numCols = Math.ceil(perPage / numRows);

  $: pdpWidth = gridWidth / numCols;
  $: pdpHeight = gridHeight / numRows;

  // color

  let globalColor: d3.ScaleSequential<string, string>;
  $: globalColor = scaleSequential()
    .domain($nice_prediction_extent)
    .interpolator(interpolateYlGnBu)
    .unknown('black');

  // header

  $: hide = !expanded || data.length === 0;
  const legendHeight = 24;

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

  function onkeydown(ev: KeyboardEvent) {
    if (ev.key === 'ArrowLeft') {
      setPage(currentPage - 1);
    } else if (ev.key === 'ArrowRight') {
      setPage(currentPage + 1);
    }
  }

  // scaling

  let scaleLocally = false;
</script>

<div class="group-container" class:hide-plots={!expanded}>
  <div class="group-header">
    <div class="toggle-and-title">
      <button on:click={toggle}>
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

    <div class="page-change" class:hide on:keydown={onkeydown} tabindex="0">
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

    <label class:hide>
      Sort by
      <select bind:value={sortingOption}>
        {#each sortingOptions as option}
          <option value={option}>{option.name}</option>
        {/each}
      </select>
    </label>

    <label class="label-and-input" class:hide>
      <input type="checkbox" bind:checked={scaleLocally} /><span
        >Scale locally</span
      >
    </label>

    {#if showColorLegend && !scaleLocally}
      <div class="legend" class:hide>
        <QuantitativeColorLegend
          width={180}
          height={legendHeight}
          color={globalColor}
          includeTitle={true}
          marginLeft={15}
          marginRight={15}
        />
      </div>
    {/if}
  </div>

  <div class="pdp-grid-container" bind:this={div}>
    {#if expanded}
      <div
        class="pdp-grid"
        style:grid-template-columns="repeat({numCols}, 1fr)"
        style:grid-template-rows="repeat({numRows}, 1fr)"
      >
        {#each pageCharts as pdp (pdp.id)}
          <PDPContainer
            {pdp}
            {globalColor}
            width={pdpWidth}
            height={pdpHeight}
            {scaleLocally}
          />
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .group-container {
    flex: 1;

    display: flex;
    flex-direction: column;
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
  }

  .pdp-grid {
    height: 100%;
    display: grid;
  }

  .group-header {
    display: flex;
    align-items: center;
    gap: 1em;
    border-top: 1px solid var(--gray-1);
    border-bottom: 1px solid var(--gray-1);
    padding-left: 0.5em;
    padding-right: 0.5em;
    padding-top: 0.25em;
    padding-bottom: 0.25em;
  }

  .hide {
    visibility: hidden;
  }

  .legend {
    margin-left: auto;
  }

  .page-change {
    display: flex;
    align-items: center;
  }

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
    transition: transform 150ms;
    transform-origin: 50% 50%;
  }

  .rotate {
    transform: rotate(-90deg);
  }
</style>
