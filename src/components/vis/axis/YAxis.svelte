<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import Label from './Label.svelte';

  export let scale:
    | d3.ScaleContinuousNumeric<any, number>
    | d3.ScaleBand<any>
    | d3.ScalePoint<any>;

  export let label: string = '';

  export let x: number = 0;
  export let y: number = 0;

  export let format = defaultFormat;

  export let gridWidth: number = 0;

  export let showAxisLabel: boolean = true;
  export let showTickLabels: boolean = true;
  export let showBaseline: boolean = false;

  export let tickLabelOutlineColor: string = 'transparent';
  export let tickColor: string = 'black';
  export let baselineColor: string = 'black';

  export let fontSize: number = 10;
  export let tickSize: number = 5;

  export let gapBetweenTickAndTickLabel: number = 2;

  export let integerOnly: boolean = false;

  export let value_map: Record<any, string> = {};

  const gapBetweenTicksAndAxisLabel: number = 30;
  const lineHeight: number = 1.2;

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
    scale: d3.ScaleContinuousNumeric<number, number>,
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
              y={scale.bandwidth() === 0 ? -scale.step() / 2 : 0}
              bold={false}
              label={value_map[tick] ?? tick}
              {fontSize}
              outlineColor={tickLabelOutlineColor}
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
      y={minimum}
      bold={true}
      {label}
      rotate={true}
      {fontSize}
    />
  {/if}
</g>

<style>
</style>
