<script lang="ts">
  import IndividualControls from './IndividualControls.svelte';
  import IndividualMain from './IndividualMain.svelte';
  import ClustersMain from './ClustersMain.svelte';
  import Tabs from './Tabs.svelte';
  import { height, mode, single_pdps, features } from '../stores';
  import ZoomedPdp from './ZoomedPDP.svelte';
  import type { DoublePDPData, SinglePDPData } from '../types';

  let zoomedPd: SinglePDPData | DoublePDPData = $single_pdps[0];
  // changing this to
  // $: selectedFeatures = $features;
  // breaks the checkbox binding. why is features being updated?
  let selectedFeatures: string[] = $features;

  function onZoom(event: CustomEvent<SinglePDPData | DoublePDPData>) {
    zoomedPd = event.detail;
    $mode = 'individual';
  }

  function onFilterByCluster(event: CustomEvent<string[]>) {
    selectedFeatures = event.detail;
    $mode = 'grid';
  }
</script>

<div class="pdp-explorer-widget-container" style:height="{$height}px">
  <Tabs />

  <div class="grid-content" class:noshow={$mode !== 'grid'}>
    <IndividualControls bind:selectedFeatures />
    <IndividualMain {selectedFeatures} on:zoom={onZoom} />
  </div>

  <div class="clusters-content" class:noshow={$mode !== 'clusters'}>
    <ClustersMain on:filterByCluster={onFilterByCluster} />
  </div>

  <div class="individual-content" class:noshow={$mode !== 'individual'}>
    <ZoomedPdp pdp={zoomedPd} on:zoom={onZoom} />
  </div>
</div>

<style>
  .pdp-explorer-widget-container {
    box-sizing: border-box;
    width: 100%;
    display: flex;
    flex-direction: column;
    font-size: 16px;
    border: 1px solid var(--gray-1);
    background-color: white;
    color: black;

    --magenta: rgb(121, 35, 103);

    --blue: rgb(0, 95, 204);

    --gray-0: rgb(247, 247, 247);
    --gray-1: rgb(226, 226, 226);
    --gray-2: rgb(198, 198, 198);
    --gray-3: rgb(171, 171, 171);
    --gray-4: rgb(145, 145, 145);
    --gray-5: rgb(119, 119, 119);
    --gray-6: rgb(94, 94, 94);
    --gray-7: rgb(71, 71, 71);
    --gray-8: rgb(48, 48, 48);
    --gray-9: rgb(27, 27, 27);

    --red: red;
  }

  .grid-content {
    flex: 1;
    min-height: 0;
    display: flex;
  }

  .clusters-content {
    flex: 1;
    min-height: 0;
  }

  .individual-content {
    flex: 1;
    min-height: 0;
  }

  /* global styles */

  .pdp-explorer-widget-container :global(canvas),
  .pdp-explorer-widget-container :global(svg) {
    display: block;
  }

  .pdp-explorer-widget-container :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    line-height: 1.2;
  }

  .pdp-explorer-widget-container :global(a) {
    color: var(--blue);
  }

  .pdp-explorer-widget-container :global(a:hover) {
    text-decoration: none;
  }

  .pdp-explorer-widget-container :global(button) {
    color: black;
    background-color: white;
    border: 1px solid black;
    border-radius: 0.25em;
    text-align: center;
    cursor: pointer;
    font-size: 1em;
    padding: 0.0625em 0.0625em;
    font-family: inherit;
  }

  .pdp-explorer-widget-container :global(button:hover:enabled) {
    background-color: var(--gray-0);
  }

  .pdp-explorer-widget-container :global(button:active:enabled) {
    background-color: var(--gray-1);
  }

  .pdp-explorer-widget-container :global(button:disabled) {
    cursor: not-allowed;
    background-color: transparent;
    color: var(--gray-4);
    border-color: var(--gray-4);
  }

  .pdp-explorer-widget-container :global(h1) {
    font-size: 1.125em;
    font-weight: 500;
  }

  .pdp-explorer-widget-container :global(.large) {
    font-size: 1.125rem;
  }

  .pdp-explorer-widget-container :global(.small) {
    font-size: 0.875rem;
  }

  .pdp-explorer-widget-container :global(.bold) {
    font-weight: 500;
  }

  .pdp-explorer-widget-container :global(.icon) {
    width: 1em;
    height: 1em;
  }

  .pdp-explorer-widget-container :global(.cutoff) {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .pdp-explorer-widget-container :global(:focus-visible) {
    outline: var(--blue) auto 1px;
  }

  .noshow {
    display: none;
  }
</style>
