<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import Label from './Label.svelte';

  export let scale:
    | d3.ScaleContinuousNumeric<number, number>
    | d3.ScaleBand<number>
    | d3.ScalePoint<number>;

  export let label: string = '';

  export let x: number = 0;
  export let y: number = 0;

  export let format = defaultFormat;

  export let gridHeight: number = 0;

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

  export let value_map: Record<number, string> = {};

  const gapBetweenTicksAndAxisLabel: number = 2;
  const lineHeight: number = 1.2;

  $: left = scale.range()[0];
  $: right = scale.range()[scale.range().length - 1];
  $: width = right - left;

  function getTicks(
    scale: d3.ScaleContinuousNumeric<number, number>,
    width: number,
    integerOnly: boolean
  ) {
    const ticks = scale.ticks(width / 80);

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
              x={scale.bandwidth() === 0 ? -scale.step() / 2 : 0}
              y={tickSize + gapBetweenTickAndTickLabel}
              bold={false}
              label={value_map[tick] ?? tick}
              outlineColor={tickLabelOutlineColor}
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
              stroke={tickLabelOutlineColor}
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
      x={left}
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
