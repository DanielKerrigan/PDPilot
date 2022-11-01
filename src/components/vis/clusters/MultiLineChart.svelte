<script lang="ts">
  import type {
    OneWayQuantitativeCluster,
    QuantitativeSinglePDPData,
  } from '../../../types';
  import { scaleLinear } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import { range } from 'd3-array';
  import YAxis from '../axis/YAxis.svelte';
  import { nice_pdp_extent } from '../../../stores';
  import { createEventDispatcher } from 'svelte';

  export let cluster: OneWayQuantitativeCluster;
  export let pds: QuantitativeSinglePDPData[];
  export let width: number;
  export let height: number;
  export let highlightPd: QuantitativeSinglePDPData | null;

  $: maxLength = Math.max(...pds.map((d) => d.mean_predictions.length));
  $: indices = range(maxLength);

  const margin = {
    top: 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: x = scaleLinear()
    .domain([indices[0], indices[indices.length - 1]])
    .range([margin.left, width - margin.right]);

  $: y = scaleLinear()
    .domain($nice_pdp_extent)
    .range([height - margin.bottom, margin.top]);

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: pdpLine = d3line<number>()
    .x((d, i) => x(i))
    .y((d, i) => y(d));

  const dispatchHover = createEventDispatcher<{
    hover: QuantitativeSinglePDPData | null;
  }>();

  function hover(pd: QuantitativeSinglePDPData | null) {
    dispatchHover('hover', pd);
  }

  const dispatchClick = createEventDispatcher<{ click: string }>();

  function click(feature: string) {
    dispatchClick('click', feature);
  }
</script>

<svg class="multi-line-chart">
  {#each pds as pd}
    <path
      tabindex="0"
      on:mouseenter={() => hover(pd)}
      on:mouseleave={() => hover(null)}
      on:focusin={() => hover(pd)}
      on:focusout={() => hover(null)}
      on:click={() => click(pd.x_feature)}
      class="line"
      d={pdpLine(pd.mean_predictions)}
      stroke="var(--black)"
      stroke-width="1.5"
      stroke-opacity="0.5"
      fill="none"
    />
  {/each}

  {#if highlightPd}
    <path
      class="line"
      d={pdpLine(highlightPd.mean_predictions)}
      stroke="var(--red)"
      stroke-width="3"
      stroke-opacity="1"
      fill="none"
      pointer-events="none"
    />
  {/if}

  <YAxis scale={y} x={margin.left} label={'average prediction'} />
</svg>

<style>
  .multi-line-chart {
    width: 100%;
    height: 100%;
  }

  .line {
    cursor: pointer;
  }

  .line:focus {
    /* the lines are effectively highlighted red when focused */
    outline: none;
  }
</style>
