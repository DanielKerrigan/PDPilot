<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import type { ScaleContinuousNumeric, ScaleBand, ScalePoint } from 'd3-scale';
  import Label from './Label.svelte';

  export let scale:
    | ScaleContinuousNumeric<number, number>
    | ScaleBand<number>
    | ScalePoint<number>;

  export let label = '';

  export let x = 0;
  export let y = 0;

  export let format = defaultFormat;

  export let gridHeight = 0;

  export let showAxisLabel = true;
  export let showTickLabels = true;
  export let showBaseline = false;

  export let tickColor = 'black';
  export let baselineColor = 'black';

  export let fontSize = 10;
  export let tickSize = 5;

  export let gapBetweenTickAndTickLabel = 2;

  export let integerOnly = false;

  export let value_map: Record<number, string> = {};

  const gapBetweenTicksAndAxisLabel = 2;
  const lineHeight = 1.2;

  $: left = scale.range()[0];
  $: right = scale.range()[scale.range().length - 1];
  $: width = right - left;

  function getTicks(
    scale: ScaleContinuousNumeric<number, number>,
    width: number,
    integerOnly: boolean
  ) {
    const ticks = scale.ticks(Math.min(width / 50, 10));

    if (integerOnly) {
      return ticks.filter(Number.isInteger);
    } else {
      return ticks;
    }
  }
</script>

<g transform="translate({x},{y})">
  <g>
    {#if showBaseline}
      <line
        x1={scale.range()[0]}
        x2={scale.range()[1]}
        stroke={baselineColor}
      />
    {/if}

    {#if 'bandwidth' in scale}
      {#each scale.domain() as tick}
        <g transform="translate({scale(tick)})">
          {#if tickSize > 0}
            <line
              y1={gridHeight}
              y2={tickSize}
              x1={scale.bandwidth() / 2}
              x2={scale.bandwidth() / 2}
              stroke={tickColor}
            />
          {/if}
          {#if showTickLabels}
            <Label
              width={scale.bandwidth() || scale.step()}
              height={fontSize * lineHeight}
              x={scale.bandwidth() === 0 ? 0 : scale.bandwidth() / 2}
              y={tickSize + gapBetweenTickAndTickLabel}
              bold={false}
              label={value_map[tick] ?? tick}
              {fontSize}
            />
          {/if}
        </g>
      {/each}
    {:else}
      {#each getTicks(scale, width, integerOnly) as tick}
        <g transform="translate({scale(tick)})">
          <line y1={gridHeight} y2={tickSize} stroke={tickColor} />
          {#if showTickLabels}
            <text
              y={tickSize + gapBetweenTickAndTickLabel}
              text-anchor="middle"
              dominant-baseline="hanging"
              font-size={fontSize}
              fill="black"
              stroke-width={2}
              paint-order="stroke"
            >
              {format(tick)}
            </text>
          {/if}
        </g>
      {/each}
    {/if}
  </g>

  {#if showAxisLabel}
    <Label
      {width}
      height={fontSize * lineHeight}
      x={width / 2 + left}
      y={tickSize +
        gapBetweenTickAndTickLabel +
        fontSize +
        gapBetweenTicksAndAxisLabel}
      bold={true}
      {label}
      {fontSize}
    />
  {/if}
</g>

<style>
</style>
