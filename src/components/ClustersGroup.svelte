<script lang="ts">
  import type { Clusters, ClustersSortingOption } from '../types';
  import { onMount } from 'svelte';
  import MultiLineChart from './vis/clusters/MultiLineChart.svelte';

  export let title: string;
  export let clusters: Clusters;
  export let sortingOptions: ClustersSortingOption[];

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  let chartWidth: number;
  let chartHeight: number;

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
  $: numClusters =
    clusters.categoricalClusters.length + clusters.quantitativeClusters.length;
  $: numRows = Math.floor(Math.sqrt(numClusters));
  $: numCols = Math.ceil(numClusters / numRows);

  $: chartWidth = gridWidth / numCols;
  $: chartHeight = gridHeight / numRows;

  // sorting

  let sortingOption = sortingOptions[0];

  $: sortedQuantitativeClusters = sortingOption.sort(
    clusters.quantitativeClusters
  );
  $: sortedCategoricalClusters = clusters.categoricalClusters;
</script>

<div class="group-container" class:hide-plots={!expanded}>
  <div class="clusters-header">
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

    <label class:hide={!expanded}>
      Sort by
      <select bind:value={sortingOption}>
        {#each sortingOptions as option}
          <option value={option}>{option.name}</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="cluster-grid-container" bind:this={div}>
    {#if expanded}
      <div
        class="cluster-grid"
        style:grid-template-columns="repeat({numCols}, 1fr)"
        style:grid-template-rows="repeat({numRows}, 1fr)"
      >
        {#each sortedQuantitativeClusters as c (c.id)}
          <MultiLineChart
            cluster={c}
            pds={clusters.quantitativePds.get(c.id) ?? []}
            width={chartWidth}
            height={chartHeight}
          />
        {/each}

        {#each sortedCategoricalClusters as c (c.id)}
          <div class="categorical-cluster">
            <div>Categorical cluster</div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .categorical-cluster {
    display: flex;
    align-items: center;
    justify-content: center;
  }

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

  .cluster-grid-container {
    flex: 1;
  }

  .cluster-grid {
    height: 100%;
    display: grid;
  }

  .clusters-header {
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

  .icon-tabler-chevron-down polyline {
    transition: transform 150ms;
    transform-origin: 50% 50%;
  }

  .rotate {
    transform: rotate(-90deg);
  }
</style>
