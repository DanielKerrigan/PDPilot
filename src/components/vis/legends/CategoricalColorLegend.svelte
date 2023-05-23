<!--
   References code from: https://observablehq.com/@d3/color-legend
   Copyright 2021, Observable Inc.
   Released under the ISC license.
 -->
<script lang="ts">
  import type { ScaleOrdinal } from 'd3-scale';

  export let width: number;
  export let height: number;
  export let color: ScaleOrdinal<number, string>;
  export let marginLeft = 0;
  export let marginRight = 0;
  export let title = '';
  export let value_map: Record<number, string> = {};

  let legendWidth = 0;

  let borderBoxSize: ResizeObserverSize[] | undefined | null;
  $: legendWidth = borderBoxSize ? borderBoxSize[0].inlineSize : 0;

  const squareSize = 12;
</script>

<div
  class="color-container"
  style:max-height="{height}px"
  style:max-width="{width}px"
  style:margin-left="{marginLeft}px"
  style:margin-right="{marginRight}px"
>
  {#if title !== ''}
    <div class="pdpilot-small pdpilot-bold">{title}:</div>
  {/if}
  <div class="swatches" style:max-width="{legendWidth}px" bind:borderBoxSize>
    {#each color.domain() as d}
      <div class="swatch-cell">
        <div
          class="swatch-square"
          style:--size="{squareSize}px"
          style:background-color={color(d)}
        />
        <div class="swatch-label pdpilot-small">{value_map[d] ?? d}</div>
      </div>
    {/each}
  </div>
</div>

<style>
  .color-container {
    display: flex;
    align-items: center;
    gap: 1em;
  }

  .swatches {
    flex: 1;
    display: flex;
    gap: 1em;
  }

  .swatch-cell {
    display: flex;
    align-items: center;
  }

  .swatch-square {
    min-width: var(--size);
    min-height: var(--size);
    margin-right: 0.25em;
  }
</style>
