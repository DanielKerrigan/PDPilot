<script lang="ts">
  import { format as d3format } from 'd3-format';
  import Label from './Label.svelte';

  export let scale:
    | d3.ScaleContinuousNumeric<number, number>
    | d3.ScaleBand<string | number>
    | d3.ScalePoint<string | number>;
  export let label: string;
  export let x: number = 0;
  export let y: number = 0;
  export let format = d3format('~s');
  export let gridHeight: number = 0;
  export let showLabels: boolean = true;
  export let fontSize: number = 10;
  export let tickSize: number = 5;

  const gapBetweenTickAndTickLabel: number = 2;
  const gapBetweenTicksAndAxisLabel: number = 2;
  const lineHeight: number = 1.2;

  $: left = scale.range()[0];
  $: right = scale.range()[scale.range().length - 1];
  $: width = right - left;
</script>

<g transform="translate({x},{y})">
  <g>
    {#if 'bandwidth' in scale}
      {#each scale.domain() as tick}
        <g transform="translate({scale(tick)})">
          <line
            y1={gridHeight}
            y2={tickSize}
            x1={scale.bandwidth() / 2}
            x2={scale.bandwidth() / 2}
            stroke="black"
          />
          {#if showLabels}
            <Label
              width={scale.bandwidth() || scale.step()}
              height={fontSize * lineHeight}
              x={scale.bandwidth() === 0 ? -scale.step() / 2 : 0}
              y={tickSize + gapBetweenTickAndTickLabel}
              bold={false}
              label={`${tick}`}
              {fontSize}
            />
          {/if}
        </g>
      {/each}
    {:else}
      {#each scale.ticks(width / 80) as tick}
        <g transform="translate({scale(tick)})">
          <line y1={gridHeight} y2={tickSize} stroke="black" />
          {#if showLabels}
            <text
              y={tickSize + gapBetweenTickAndTickLabel}
              text-anchor="middle"
              dominant-baseline="hanging"
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
</g>

<style>
</style>
