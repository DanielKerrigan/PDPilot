<script lang="ts">
  import type { SinglePDPData, DoublePDPData } from '../types';
  import { createEventDispatcher, onMount } from 'svelte';
  import { single_pdps } from '../stores';
  import PDP from './PDP.svelte';

  export let pdp: SinglePDPData | DoublePDPData;
  export let globalColor: d3.ScaleSequential<string, string>;
  export let scaleLocally: boolean;
  export let showTrendLine: boolean;

  // header

  const headerHeight = 30;

  $: title =
    pdp.num_features === 1
      ? pdp.x_feature
      : `${pdp.x_feature} vs. ${pdp.y_feature}`;

  let showMarginalDistribution: boolean = false;
  let show1D: boolean = false;
  let showInteractions: boolean = false;

  // sizes

  let div: HTMLDivElement;

  let gridWidth: number;
  let gridHeight: number;

  $: halfWidth = gridWidth / 2;
  $: halfHeight = gridHeight / 2;

  onMount(() => {
    // Adapted from https://blog.sethcorker.com/question/how-do-you-use-the-resize-observer-api-in-svelte/
    const resizeObserver = new ResizeObserver(
      (entries: ResizeObserverEntry[]) => {
        if (entries.length !== 1) {
          return;
        }

        const entry: ResizeObserverEntry = entries[0];

        if (entry.borderBoxSize.length !== 1) {
          return;
        }

        const contentRect: ResizeObserverSize = entry.borderBoxSize[0];

        gridWidth = contentRect.inlineSize;
        gridHeight = contentRect.blockSize;
      }
    );

    resizeObserver.observe(div);

    return () => resizeObserver.unobserve(div);
  });

  let xPdp: SinglePDPData;
  let yPdp: SinglePDPData;

  $: if (pdp.num_features === 2) {
    let found = 0;

    for (let pd of $single_pdps) {
      if (pd.x_feature === pdp.x_feature) {
        found++;
        xPdp = pd;
      } else if (pd.x_feature === pdp.y_feature) {
        found++;
        yPdp = pd;
      }

      if (found === 2) {
        break;
      }
    }
  }

  function shouldShow1D(
    show1D: boolean,
    xPdp: SinglePDPData | undefined,
    yPdp: SinglePDPData | undefined
  ) {
    return show1D && xPdp !== undefined && yPdp !== undefined;
  }

  // closing

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }
</script>

<div class="zoomed-pdp-background">
  <div class="zoomed-pdp-header" style="min-height: {headerHeight}px;">
    <div>{title}</div>

    <label class="label-and-input">
      <input type="checkbox" bind:checked={scaleLocally} />
      Scale locally
    </label>

    {#if pdp.num_features === 1 && pdp.kind === 'quantitative'}
      <label class="label-and-input">
        <input type="checkbox" bind:checked={showTrendLine} />
        Trend line
      </label>
    {/if}

    <label class="label-and-input">
      <input type="checkbox" bind:checked={showMarginalDistribution} />
      {pdp.num_features === 1
        ? 'Marginal distribution'
        : 'Marginal distributions'}
    </label>

    {#if pdp.num_features === 2}
      <label class="label-and-input">
        <input type="checkbox" bind:checked={show1D} />
        1D PDPs
      </label>

      <label class="label-and-input">
        <input type="checkbox" bind:checked={showInteractions} />
        Interaction
      </label>
    {/if}

    <button class="close-button" on:click={close}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="icon icon-tabler icon-tabler-x"
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
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
  <div
    class="zoomed-pdp-content show1D-{shouldShow1D(
      show1D,
      xPdp,
      yPdp
    )}-showInteraction-{showInteractions}"
    bind:this={div}
  >
    {#if shouldShow1D(show1D, xPdp, yPdp)}
      <div style:grid-area="one-way-left">
        <PDP
          pdp={xPdp}
          {globalColor}
          width={halfWidth}
          height={halfHeight}
          {scaleLocally}
          {showTrendLine}
          {showMarginalDistribution}
        />
      </div>

      <div style:grid-area="one-way-right">
        <PDP
          pdp={yPdp}
          {globalColor}
          width={halfWidth}
          height={halfHeight}
          {scaleLocally}
          {showTrendLine}
          {showMarginalDistribution}
        />
      </div>
    {/if}

    <div style:grid-area="two-way">
      <PDP
        {pdp}
        {globalColor}
        width={shouldShow1D(show1D, xPdp, yPdp) && showInteractions
          ? halfWidth
          : gridWidth}
        height={shouldShow1D(show1D, xPdp, yPdp) || showInteractions
          ? halfHeight
          : gridHeight}
        {scaleLocally}
        {showTrendLine}
        {showMarginalDistribution}
        showColorLegend={true}
      />
    </div>

    {#if showInteractions}
      <div style:grid-area="interaction">
        <PDP
          {pdp}
          {globalColor}
          width={shouldShow1D(show1D, xPdp, yPdp) ? halfWidth : gridWidth}
          height={halfHeight}
          {scaleLocally}
          {showTrendLine}
          {showMarginalDistribution}
          showInteractions={true}
          showColorLegend={true}
        />
      </div>
    {/if}
  </div>
</div>

<style>
  .zoomed-pdp-background {
    position: absolute;

    left: 0;
    top: 0;

    z-index: 1;

    width: 100%;
    height: 100%;

    background-color: white;

    display: flex;
    flex-direction: column;

    border: 1px solid var(--gray-1);
  }

  .zoomed-pdp-header {
    display: flex;
    align-items: center;
    gap: 2em;
    background-color: white;
    padding-left: 0.25em;
    padding-right: 0.25em;
    border-bottom: 1px solid var(--gray-1);
  }

  .zoomed-pdp-content {
    flex: 1;
    display: grid;
  }

  .close-button {
    margin-left: auto;
  }

  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .show1D-true-showInteraction-true {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'two-way interaction';
  }

  .show1D-true-showInteraction-false {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'one-way-left one-way-right'
      'two-way two-way';
  }

  .show1D-false-showInteraction-true {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'two-way two-way'
      'interaction interaction';
  }

  .show1D-false-showInteraction-false {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      'two-way two-way'
      'two-way two-way';
  }
</style>
