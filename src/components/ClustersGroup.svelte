<script lang="ts">
  import type {
    Clusters,
    TwoWayPD,
    OneWayCategoricalCluster,
    OneWayQuantitativeCluster,
    OrderedOneWayPD,
    OneWayPD,
  } from '../types';
  import { createEventDispatcher, onMount } from 'svelte';
  import MultiLineChart from './vis/pdp-clusters/MultiLineChart.svelte';
  import CategoryMosaic from './vis/pdp-clusters/CategoryMosaic.svelte';

  export let title: string;
  export let clusters: Clusters;

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
  // TODO: https://stackoverflow.com/questions/60104268/default-panel-layout-of-ggplot2facet-wrap
  $: numRows = Math.floor(Math.sqrt(numClusters));
  $: numCols = Math.ceil(numClusters / numRows);

  $: chartWidth = gridWidth / numCols;
  $: chartHeight = gridHeight / numRows;

  $: allClusters = [
    ...clusters.quantitativeClusters,
    ...clusters.categoricalClusters,
  ];

  $: isClusterExpanded = Object.fromEntries(
    allClusters.map((d) => [d.id, false])
  );

  function toggleClusterExpanded(id: number) {
    isClusterExpanded[id] = !isClusterExpanded[id];
  }

  // highlighting

  let highlightPd: OneWayPD | TwoWayPD | null = null;

  function setHighlight(cluster: number, feature: string) {
    const pds = (clusters.quantitativePds.get(cluster) ??
      clusters.categoricalPds.get(cluster) ??
      []) as OneWayPD[];

    highlightPd = pds.find((pd) => pd.x_feature === feature) ?? null;
  }

  function resetHighlight() {
    highlightPd = null;
  }

  function onLineHover(event: CustomEvent<OrderedOneWayPD | null>) {
    highlightPd = event.detail;
  }

  function onLineClick(event: CustomEvent<string>) {
    onClickFeature(event.detail);
  }

  // events

  const clusterDispatch = createEventDispatcher<{
    filterByCluster: string[];
  }>();

  function onClickCluster(
    cluster: OneWayCategoricalCluster | OneWayQuantitativeCluster
  ) {
    clusterDispatch('filterByCluster', cluster.features);
  }

  const zoomDispatch = createEventDispatcher<{
    zoom: OneWayPD | TwoWayPD;
  }>();

  function onClickFeature(feature: string) {
    if (highlightPd && highlightPd.x_feature === feature) {
      zoomDispatch('zoom', highlightPd);
    }
  }
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
  </div>

  <div class="cluster-grid-container">
    {#if expanded}
      <div class="cluster-grid-side">
        <ul class="clusters-list">
          {#each allClusters as c (c.id)}
            <li class="cluster-list-item">
              <div class="cluster-id">
                <button on:click={() => toggleClusterExpanded(c.id)}>
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
                    <polyline
                      points={'6 9 12 15 18 9'}
                      class:rotate={!isClusterExpanded[c.id]}
                    />
                  </svg>
                </button>
                <span>Cluster {c.id + 1}</span>
              </div>

              {#if isClusterExpanded[c.id]}
                <ul>
                  {#each c.features as feature}
                    <li
                      class="cluster-feature-list-item cutoff small"
                      title={feature}
                      tabindex="0"
                      on:mouseenter={() => setHighlight(c.id, feature)}
                      on:mouseleave={() => resetHighlight()}
                      on:focusin={() => setHighlight(c.id, feature)}
                      on:focusout={() => resetHighlight()}
                      on:click={() => onClickFeature(feature)}
                      class:highlight-feature={highlightPd &&
                        highlightPd.num_features === 1 &&
                        highlightPd.cluster === c.id &&
                        highlightPd.x_feature === feature}
                    >
                      {feature}
                    </li>
                  {/each}
                </ul>
              {/if}
            </li>
          {/each}
        </ul>
      </div>
    {/if}

    <div class="cluster-grid-main" bind:this={div}>
      {#if expanded}
        <div
          class="cluster-grid"
          style:grid-template-columns="repeat({numCols}, {chartWidth}px)"
          style:grid-template-rows="repeat({numRows}, {chartHeight}px)"
        >
          {#each clusters.quantitativeClusters as c (c.id)}
            <div class="cluster-container">
              <button on:click={() => onClickCluster(c)}
                >Cluster {c.id + 1}</button
              >
              <MultiLineChart
                on:hover={onLineHover}
                on:click={onLineClick}
                cluster={c}
                pds={clusters.quantitativePds.get(c.id) ?? []}
                width={chartWidth}
                height={chartHeight}
                highlightPd={highlightPd &&
                highlightPd.num_features === 1 &&
                highlightPd.kind === 'quantitative' &&
                highlightPd.cluster === c.id
                  ? highlightPd
                  : null}
              />
            </div>
          {/each}

          {#each clusters.categoricalClusters as c (c.id)}
            <div class="cluster-container">
              <button on:click={() => onClickCluster(c)}
                >Cluster {c.id + 1}</button
              >
              <CategoryMosaic
                cluster={c}
                pds={clusters.categoricalPds.get(c.id) ?? []}
                width={chartWidth}
                height={chartHeight}
              />
            </div>
          {/each}
        </div>
      {/if}
    </div>
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

  .cluster-grid-container {
    flex: 1;
    display: flex;

    min-height: 0;
  }

  .cluster-grid-side {
    flex: 0 0 200px;
    min-width: 200px;
    padding: 0.25em;
    border-right: 1px solid var(--gray-1);
  }

  .clusters-list {
    max-height: 100%;
    overflow-y: scroll;
  }

  .cluster-grid-main {
    flex: 1;
  }

  .cluster-grid {
    height: 100%;
    display: grid;
  }

  .clusters-header {
    height: 2em;
    display: flex;
    align-items: center;
    gap: 1em;
    border-top: 1px solid var(--gray-1);
    border-bottom: 1px solid var(--gray-1);
    padding-left: 0.5em;
    padding-right: 0.5em;
  }

  .icon-tabler-chevron-down polyline {
    transition: transform 150ms;
    transform-origin: 50% 50%;
  }

  .rotate {
    transform: rotate(-90deg);
  }

  ul {
    list-style: none;
  }

  .cluster-id {
    display: flex;
    align-items: center;
  }

  .cluster-id > button {
    border-color: transparent;
  }

  .cluster-list-item + .cluster-list-item {
    margin-top: 0.5em;
  }

  .cluster-feature-list-item {
    cursor: pointer;
    margin-left: 1.25em;
  }

  /* the focus style is applied in .highlight-feature */
  .cluster-feature-list-item:focus {
    outline: none;
  }

  .highlight-feature {
    text-decoration: underline;
  }
</style>
