<script lang="ts">
  import Tabs from './Tabs.svelte';
  import { height, selectedTab } from '../stores';
  import DetailedPlot from './DetailedPlot.svelte';
  import OneWayGridContainer from './OneWayGridContainer.svelte';
  import TwoWayGridContainer from './TwoWayGridContainer.svelte';
</script>

<div class="pdp-explorer-widget-container" style:height="{$height}px">
  <Tabs />

  <div
    class="pdp-tab-content"
    class:pdp-hide={$selectedTab !== 'one-way-plots'}
  >
    <OneWayGridContainer />
  </div>

  <div
    class="pdp-tab-content"
    class:pdp-hide={$selectedTab !== 'two-way-plots'}
  >
    <TwoWayGridContainer />
  </div>

  <div
    class="pdp-tab-content"
    class:pdp-hide={$selectedTab !== 'detailed-plot'}
  >
    <DetailedPlot />
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
    --black: black;

    --red: #d62728;
  }

  .pdp-tab-content {
    flex: 1;
    min-height: 0;
  }

  /* global styles */

  .pdp-explorer-widget-container :global(.pdp-hide) {
    display: none;
  }

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

  .pdp-explorer-widget-container :global(h2) {
    font-size: 1.0625em;
    font-weight: 500;
  }

  .pdp-explorer-widget-container :global(.large) {
    font-size: 1.125em;
  }

  .pdp-explorer-widget-container :global(.small) {
    font-size: 0.875em;
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

  /* https://stackoverflow.com/a/69029387/5016634 */
  .pdp-explorer-widget-container :global(.icon-tabler) {
    -webkit-transform: translate(0px, 0px);
    transform: translate(0px, 0px);
  }
</style>
