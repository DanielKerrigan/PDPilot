<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import Label from './Label.svelte';

  export let scale:
    | d3.ScaleContinuousNumeric<number, number>
    | d3.ScaleBand<string | number>
    | d3.ScalePoint<string | number>;
  export let label: string;
  export let x: number = 0;
  export let y: number = 0;
  export let format = defaultFormat;
  export let gridWidth: number = 0;
  export let showLabels: boolean = true;
  export let fontSize: number = 10;
  export let tickSize: number = 5;

  const gapBetweenTickAndTickLabel: number = 2;
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
</script>

<g transform="translate({x},{y})">
  <g>
    {#if 'bandwidth' in scale}
      {#each scale.domain() as tick (tick)}
        <g transform="translate(0,{scale(tick)})">
          <line
            y1={scale.bandwidth() / 2}
            y2={scale.bandwidth() / 2}
            x1={-tickSize}
            x2={gridWidth}
            stroke="black"
          />
          {#if showLabels}
            <Label
              width={scale.bandwidth() || scale.step()}
              height={fontSize * lineHeight}
              x={-(tickSize + fontSize + gapBetweenTickAndTickLabel)}
              y={scale.bandwidth() === 0 ? -scale.step() / 2 : 0}
              bold={false}
              label={`${tick}`}
              {fontSize}
              rotate={true}
            />
          {/if}
        </g>
      {/each}
    {:else}
      {#each scale.ticks(Math.min(height / 30, 10)) as tick}
        <g transform="translate(0,{scale(tick)})">
          <line x1={-tickSize} x2={gridWidth} stroke="black" />
          {#if showLabels}
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
</g>

<style>
</style>
