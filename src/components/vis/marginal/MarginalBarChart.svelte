<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import { range, rollup } from 'd3-array';
  import type { ScalePoint, ScaleBand } from 'd3-scale';

  export let data: { bins: number[]; counts: number[] };
  export let height: number;
  export let direction: 'vertical' | 'horizontal';
  export let x: ScalePoint<number> | ScaleBand<number>;
  export let translate: [number, number] = [0, 0];
  export let highlightedValues: number[] = [];

  $: indices = range(data.counts.length);

  $: highlightedCounts = rollup(
    highlightedValues,
    (g) => g.length,
    (d) => d
  );

  $: y = scaleLinear()
    .domain([0, Math.max(...data.counts)])
    .range(direction === 'horizontal' ? [height, 0] : [0, height]);

  $: barWidth = (x.bandwidth() || x.step() * x.padding()) - 2;
  $: offset = (x.bandwidth() === 0 ? barWidth / 2 : 0) - 1;
</script>

<g transform="translate({translate})">
  {#if direction === 'horizontal'}
    {#each indices as i}
      <rect
        x={(x(data.bins[i]) ?? 0) - offset}
        y={y(data.counts[i])}
        width={barWidth}
        height={y(0) - y(data.counts[i])}
        fill="var(--gray-3)"
      />

      {#if highlightedValues.length > 0}
        <rect
          x={(x(data.bins[i]) ?? 0) - offset}
          y={y(highlightedCounts.get(data.bins[i]) ?? 0)}
          width={barWidth}
          height={y(0) - y(highlightedCounts.get(data.bins[i]) ?? 0)}
          fill="red"
        />
      {/if}
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
        y={(x(data.bins[i]) ?? 0) - offset}
        width={y(data.counts[i])}
        height={barWidth}
        fill="var(--gray-3)"
      />

      {#if highlightedValues.length > 0}
        <rect
          x={0}
          y={(x(data.bins[i]) ?? 0) - offset}
          width={y(highlightedCounts.get(data.bins[i]) ?? 0)}
          height={barWidth}
          fill="red"
        />
      {/if}
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
