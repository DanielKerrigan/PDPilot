<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import type { ScaleLinear } from 'd3-scale';
  import { range } from 'd3-array';

  export let data: { bins: number[]; counts: number[] };
  export let height: number;
  export let direction: 'vertical' | 'horizontal';
  export let x: ScaleLinear<number, number>;
  export let translate: [number, number] = [0, 0];
  export let fill = 'var(--gray-3)';

  $: indices = range(data.counts.length);

  $: y = scaleLinear()
    .domain([0, Math.max(...data.counts)])
    .range(direction === 'horizontal' ? [height, 0] : [0, height]);
</script>

<g transform="translate({translate})">
  {#if direction === 'horizontal'}
    {#each indices as i}
      <rect
        x={x(data.bins[i]) + 1}
        y={y(data.counts[i])}
        width={x(data.bins[i + 1]) - x(data.bins[i]) - 2}
        height={y(0) - y(data.counts[i])}
        {fill}
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
        width={y(data.counts[i])}
        height={x(data.bins[i]) - x(data.bins[i + 1]) - 2}
        {fill}
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

<style>
</style>
