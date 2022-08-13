<script lang="ts">
  import type { CategoricalMarginalDistribution } from '../../../types';
  import { scaleLinear } from 'd3-scale';
  import { range } from 'd3-array';

  export let data: CategoricalMarginalDistribution;
  export let height: number;
  export let direction: 'vertical' | 'horizontal';
  export let x: d3.ScalePoint<string | number> | d3.ScaleBand<string | number>;
  export let translate: [number, number] = [0, 0];

  $: indices = range(data.counts.length);

  $: y = scaleLinear()
    .domain([0, Math.max(...data.counts)])
    .range(direction === 'horizontal' ? [height, 0] : [0, height]);

  $: barWidth = (x.bandwidth() || x.step() * x.padding()) - 2;
  $: offset = (x.bandwidth() === 0 ? (barWidth / 2) : 0) - 1;
</script>

<g transform="translate({translate})">
  {#if direction === 'horizontal'}
    {#each indices as i}
      <rect
        x={(x(data.bins[i]) ?? 0) - offset}
        y={y(data.counts[i])}
        width={barWidth}
        height={y(0) - y(data.counts[i])}
      />
    {/each}
    <line
      x1={x.range()[0]}
      x2={x.range()[1]}
      y1={height}
      y2={height}
    />
  {:else}
    {#each indices as i}
      <rect
        x={0}
        y={(x(data.bins[i]) ?? 0) - offset}
        width={y(data.counts[i])}
        height={barWidth}
      />
    {/each}
    <line
      x1={0}
      x2={0}
      y1={x.range()[0]}
      y2={x.range()[1]}
    />
  {/if}
</g>

<style>
  rect {
    fill: var(--gray-4);
  }

  line {
    stroke: var(--gray-1);
  }
</style>