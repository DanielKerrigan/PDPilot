<svelte:options namespace="svg" />

<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import { range } from 'd3-array';
  import { line as d3line } from 'd3-shape';
  import type { ScaleLinear, ScaleBand } from 'd3-scale';
  import type { OneWayPD } from '../../../types';
  import { one_way_pdp_extent } from '../../../stores';

  export let pd: OneWayPD;
  export let height: number;
  export let direction: 'vertical' | 'horizontal';
  export let x: ScaleBand<number> | ScaleLinear<number, number>;
  export let translate: [number, number] = [0, 0];
  export let stroke = 'black';

  $: I = range(pd.x_values.length);

  $: y = scaleLinear()
    .domain($one_way_pdp_extent)
    .range(direction === 'horizontal' ? [height, 0] : [0, height]);

  $: xAccessor = (i: number) =>
    'bandwidth' in x
      ? (x(pd.x_values[i]) ?? 0) + x.bandwidth() / 2
      : x(pd.x_values[i]);

  $: yAccessor = (i: number) => y(pd.mean_predictions[i]);

  $: line = d3line<number>()
    .x(direction === 'horizontal' ? xAccessor : yAccessor)
    .y(direction === 'horizontal' ? yAccessor : xAccessor);

  $: radius = 'bandwidth' in x ? Math.min(2, x.bandwidth() / 2) : 0;
</script>

<g transform="translate({translate})">
  <path d={line(I)} {stroke} fill="none" />
  {#if 'bandwidth' in x}
    {#each I as i}
      <circle
        cx={direction === 'horizontal' ? xAccessor(i) : yAccessor(i)}
        cy={direction === 'horizontal' ? yAccessor(i) : xAccessor(i)}
        r={radius}
        fill={stroke}
      />
    {/each}
  {/if}
</g>

<style>
</style>
