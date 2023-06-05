<svelte:options namespace="svg" />

<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import type { ScaleLinear } from 'd3-scale';
  import { range } from 'd3-array';
  import type { Distribution } from '../../../types';

  export let data: Distribution;
  export let height: number;
  export let direction: 'vertical' | 'horizontal';
  export let x: ScaleLinear<number, number>;
  export let translate: [number, number] = [0, 0];
  export let fill = 'var(--gray-3)';
  export let stroke = 'none';
  export let unit: 'count' | 'percent' = 'count';

  export let maxValue = 0;

  $: maxY = maxValue
    ? maxValue
    : unit === 'count'
    ? Math.max(...data.counts)
    : Math.max(...data.percents);

  function getCount(data: Distribution, i: number): number {
    return data.counts[i];
  }

  function getPercent(data: Distribution, i: number): number {
    return data.percents[i];
  }

  $: accessor = unit === 'count' ? getCount : getPercent;

  $: indices = range(data.counts.length);

  $: y = scaleLinear()
    .domain([0, maxY])
    .range(direction === 'horizontal' ? [height, 0] : [0, height]);
</script>

<!-- don't draw rects with negative dimensions -->
{#if height > 0 && Math.min(...x.range()) >= 0 && Math.max(...x.range()) > 0}
  <g transform="translate({translate})">
    {#if direction === 'horizontal'}
      {#each indices as i}
        <rect
          x={x(data.bins[i]) + 1}
          y={y(accessor(data, i))}
          width={x(data.bins[i + 1]) - x(data.bins[i]) - 2}
          height={y(0) - y(accessor(data, i))}
          {fill}
          {stroke}
        />
      {/each}
      <line
        x1={x.range()[0]}
        x2={x.range()[1]}
        y1={height}
        y2={height}
        stroke="var(--gray-1)"
      />
    {:else}
      {#each indices as i}
        <rect
          x={0}
          y={x(data.bins[i + 1]) + 1}
          width={y(accessor(data, i))}
          height={x(data.bins[i]) - x(data.bins[i + 1]) - 2}
          {fill}
          {stroke}
        />
      {/each}
      <line
        x1={0}
        x2={0}
        y1={x.range()[0]}
        y2={x.range()[1]}
        stroke="var(--gray-1)"
      />
    {/if}
  </g>
{/if}

<style>
</style>
