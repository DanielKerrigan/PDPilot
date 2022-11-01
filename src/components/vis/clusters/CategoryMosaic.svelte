<script lang="ts">
  import type {
    OneWayCategoricalCluster,
    CategoricalSinglePDPData,
  } from '../../../types';
  import { scaleLinear, scaleBand, scalePoint } from 'd3-scale';
  import { range } from 'd3-array';
  import { nice_pdp_extent } from '../../../stores';

  export let cluster: OneWayCategoricalCluster;
  export let pds: CategoricalSinglePDPData[];
  export let width: number;
  export let height: number;

  $: filteredPds = pds.slice(0, 8);
  $: numPlots = filteredPds.length;

  // TODO: https://stackoverflow.com/questions/60104268/default-panel-layout-of-ggplot2facet-wrap
  $: numRows = Math.floor(Math.sqrt(numPlots));
  $: numCols = Math.ceil(numPlots / numRows);

  $: maxLength = Math.max(...filteredPds.map((d) => d.mean_predictions.length));
  $: indices = range(maxLength);

  function getRow(i: number) {
    return Math.floor(i / numCols);
  }

  function getCol(i: number) {
    return i % numCols;
  }

  const margin = {
    top: 10,
    right: 10,
    bottom: 40,
    left: 50,
  };

  $: fx = scaleBand<number>()
    .domain(range(numCols))
    .range([margin.left, width - margin.right]);

  $: fy = scaleBand<number>()
    .domain(range(numRows))
    .range([margin.top, height - margin.bottom]);

  $: x = scalePoint<number>()
    .domain(indices)
    .range([0, fx.bandwidth()])
    .padding(0.5);

  $: y = scaleLinear().domain($nice_pdp_extent).range([fy.bandwidth(), 0]);

  $: radius = Math.min(3, x.step() / 2 - 1);
</script>

<svg class="category-mosaic">
  {#each filteredPds as pd, i}
    <g transform="translate({fx(getCol(i))},{fy(getRow(i))})">
      <rect
        width={fx.bandwidth()}
        height={fy.bandwidth()}
        fill="none"
        stroke="var(--gray-0)"
      />

      {#each pd.mean_predictions as pred, i}
        <circle cx={x(i)} cy={y(pred)} r={radius} fill="var(--black)" />
      {/each}
    </g>
  {/each}
</svg>

<style>
  .category-mosaic {
    width: 100%;
    height: 100%;
  }
</style>
