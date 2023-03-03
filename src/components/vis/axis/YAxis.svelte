<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import type { ScaleContinuousNumeric, ScaleBand, ScalePoint } from 'd3-scale';
  import Label from './Label.svelte';

  export let scale:
    | ScaleContinuousNumeric<any, number>
    | ScaleBand<any>
    | ScalePoint<any>;

  export let label = '';

  export let x = 0;
  export let y = 0;

  export let format = defaultFormat;

  export let gridWidth = 0;

  export let showAxisLabel = true;
  export let showTickLabels = true;
  export let showBaseline = false;

  export let tickColor = 'black';
  export let baselineColor = 'black';

  export let fontSize = 10;
  export let tickSize = 5;

  export let gapBetweenTickAndTickLabel = 2;

  export let integerOnly = false;

  export let value_map: Record<any, string> = {};

  const gapBetweenTicksAndAxisLabel = 30;
  const lineHeight = 1.2;

  $: minimum = Math.min(
    scale.range()[0],
    scale.range()[scale.range().length - 1]
  );
  $: maximum = Math.max(
    scale.range()[0],
    scale.range()[scale.range().length - 1]
  );
  $: height = maximum - minimum;

  function getTicks(
    scale: ScaleContinuousNumeric<number, number>,
    height: number,
    integerOnly: boolean
  ) {
    const ticks = scale.ticks(Math.min(height / 30, 10));

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
        y1={scale.range()[0]}
        y2={scale.range()[1]}
        stroke={baselineColor}
      />
    {/if}

    {#if 'bandwidth' in scale}
      {#each scale.domain() as tick (tick)}
        <g transform="translate(0,{scale(tick)})">
          {#if tickSize > 0}
            <line
              y1={scale.bandwidth() / 2}
              y2={scale.bandwidth() / 2}
              x1={-tickSize}
              x2={gridWidth}
              stroke={tickColor}
            />
          {/if}
          {#if showTickLabels}
            <Label
              width={scale.bandwidth() || scale.step()}
              height={fontSize * lineHeight}
              x={-(tickSize + fontSize + gapBetweenTickAndTickLabel)}
              y={scale.bandwidth() === 0 ? 0 : scale.bandwidth() / 2}
              bold={false}
              label={value_map[tick] ?? tick}
              {fontSize}
              rotate={true}
            />
          {/if}
        </g>
      {/each}
    {:else}
      {#each getTicks(scale, height, integerOnly) as tick}
        <g transform="translate(0,{scale(tick)})">
          <line x1={-tickSize} x2={gridWidth} stroke={tickColor} />
          {#if showTickLabels}
            <text
              x={-tickSize - gapBetweenTickAndTickLabel}
              text-anchor="end"
              dominant-baseline="middle"
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
      width={height}
      height={fontSize * lineHeight}
      x={-(
        tickSize +
        gapBetweenTickAndTickLabel +
        fontSize +
        gapBetweenTicksAndAxisLabel
      )}
      y={height / 2 + minimum}
      bold={true}
      {label}
      rotate={true}
      {fontSize}
    />
  {/if}
</g>

<style>
</style>
