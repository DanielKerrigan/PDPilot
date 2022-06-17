<script lang="ts">
  import type { PDPData } from '../types';
  import PDP from './PDP.svelte';
  import { scaleSequential } from 'd3-scale';
  import { interpolateBuPu } from 'd3-scale-chromatic';
  import QuantitativeColorLegend from './QuantitativeColorLegend.svelte';

  export let title: string;
  export let data: PDPData[];
  export let predictionExtent: [number, number];
  export let showColorLegend: boolean = false;
  export let expanded: boolean = true;
  export let otherSectionCollapsed: boolean = false;

  // expand and collapse

  function expand() {
    expanded = true;
  }

  function collapse() {
    expanded = false;
  }

  // number of rows and columns

  const maxNumCols = 5;
  $: maxNumRows = otherSectionCollapsed ? 4 : 2;
  $: numRows = Math.min(maxNumRows, Math.ceil(data.length / maxNumCols));
  $: numCols = Math.min(maxNumCols, Math.ceil(data.length / numRows));

  // pagination

  let currentPage = 1;

  $: perPage = maxNumRows * maxNumCols;
  $: numPages = Math.ceil(data.length / perPage);

  $: pageCharts = data.slice(
    (currentPage - 1) * currentPage,
    (currentPage - 1) * currentPage + perPage
  );

  // color

  let color: d3.ScaleSequential<string, string>;
  $: color = scaleSequential()
    .domain(predictionExtent)
    .interpolator(interpolateBuPu)
    .unknown('black');

  // header

  const headerHeight = 30;
</script>

<div
  class="group-container"
  class:hide-plots={!expanded}
  style="min-height: {headerHeight}px;"
>
  <div class="header" style="height: {headerHeight}px;">
    <div>
      {#if expanded}
        <button on:click={collapse}>
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
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
      {:else}
        <button on:click={expand}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="icon icon-tabler icon-tabler-chevron-right"
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
            <polyline points="9 6 15 12 9 18" />
          </svg>
        </button>
      {/if}
    </div>

    <div class="group-title">{title}</div>

    {#if expanded}
      <div class="page-change">
        <button
          disabled={currentPage === 1}
          on:click={() => (currentPage -= 1)}
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
          disabled={currentPage === numPages}
          on:click={() => (currentPage += 1)}
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

      {#if showColorLegend}
        <div class="legend">
          <QuantitativeColorLegend width={200} height={headerHeight} {color} />
        </div>
      {/if}
    {/if}
  </div>

  {#if expanded}
    <div
      class="grid"
      style="grid-template-columns: repeat({numCols}, 1fr); grid-template-rows: repeat({numRows}, 1fr);"
    >
      {#each pageCharts as pdp (pdp.id)}
        <PDP {pdp} {predictionExtent} {color} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .group-container {
    flex: 1;

    display: flex;
    flex-direction: column;
  }

  .group-title {
    width: 110px;
  }

  .hide-plots {
    flex: 0;
  }

  .grid {
    display: grid;
    flex: 1;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 0.5em;
    background-color: var(--light-gray);
    border-top: 1px solid var(--medium-gray);
    padding-left: 0.25em;
    padding-right: 0.25em;
  }

  .legend {
    margin-left: auto;
  }

  .icon-tabler-chevron-down,
  .icon-tabler-chevron-right {
    cursor: pointer;
  }

  .page-change {
    display: flex;
    align-items: center;
  }

  .current-page-number {
    width: 2em;
    text-align: center;
  }
</style>
