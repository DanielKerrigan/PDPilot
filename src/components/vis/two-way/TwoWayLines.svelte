<script lang="ts">
  import {
    scaleLinear,
    scalePoint,
    scaleSequential,
    scaleOrdinal,
  } from 'd3-scale';
  import type { ScaleSequential, ScaleOrdinal } from 'd3-scale';
  import type { Line } from 'd3-shape';
  import { line as d3line } from 'd3-shape';
  import { quantize } from 'd3-interpolate';
  import { interpolateViridis, schemeTableau10 } from 'd3-scale-chromatic';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import { onMount } from 'svelte';
  import { scaleCanvas } from '../../../vis-utils';
  import QuantitativeColorLegend from '../legends/QuantitativeColorLegend.svelte';
  import type { FeatureInfo, TwoWayPD } from '../../../types';
  import { feature_info, two_way_pdp_extent } from '../../../stores';
  import CategoricalColorLegend from '../legends/CategoricalColorLegend.svelte';

  export let pd: TwoWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showColorLegend: boolean;
  export let marginTop = 0;
  export let marginRight = 0;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  function getColorScale(
    yFeature: FeatureInfo
  ): ScaleSequential<string> | ScaleOrdinal<number, string> {
    if (yFeature.kind === 'quantitative') {
      return scaleSequential()
        .domain([
          yFeature.values[0],
          yFeature.values[yFeature.values.length - 1],
        ])
        .interpolator((t) => interpolateViridis(1 - t));
    } else if (
      yFeature.kind === 'categorical' &&
      (yFeature.subkind === 'nominal' || yFeature.subkind === 'one_hot')
    ) {
      const n = yFeature.values.length;
      return scaleOrdinal<number, string>()
        .domain(yFeature.values)
        .range(
          n <= 10 ? schemeTableau10 : quantize(interpolateViridis, n).reverse()
        );
    } else {
      const n = yFeature.values.length;
      return scaleOrdinal<number, string>()
        .domain(yFeature.values)
        .range(quantize(interpolateViridis, n).reverse());
    }
  }

  $: legendHeight = showColorLegend ? 24 : 0;
  $: heightExcludingLegend = height - legendHeight;

  $: margin = {
    top: marginTop,
    right: marginRight,
    bottom: 35,
    left: 50,
  };

  $: xFeature = $feature_info[pd.x_feature];
  $: yFeature = $feature_info[pd.y_feature];

  $: localY = scaleLinear()
    .domain([pd.pdp_min, pd.pdp_max])
    .range([heightExcludingLegend - margin.bottom, margin.top]);

  $: globalY = scaleLinear()
    .domain($two_way_pdp_extent)
    .range([heightExcludingLegend - margin.bottom, margin.top]);

  $: y = scaleLocally ? localY : globalY;

  $: x =
    xFeature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_values[0], pd.x_values[pd.x_values.length - 1]])
          .range([margin.left, width - margin.right])
      : scalePoint<number>()
          .domain(pd.x_values)
          .range([margin.left, width - margin.right])
          .padding(0.5);

  $: color = getColorScale(yFeature);

  type Point = { x: number; prediction: number };
  type TwoWayLineData = { y: number; values: Point[] }[];

  $: line = d3line<Point>()
    .x((d) => x(d.x) ?? 0)
    .y((d) => y(d.prediction))
    .context(ctx);

  $: data = getLines(pd);

  function getLines(pd: TwoWayPD): TwoWayLineData {
    const lines = new Map<number, Point[]>();

    for (let i = 0; i < pd.mean_predictions.length; i++) {
      const x = pd.x_values[i];
      const y = pd.y_values[i];
      const prediction = pd.mean_predictions[i];

      const values = lines.get(y) ?? [];
      values.push({ x, prediction });
      lines.set(y, values);
    }

    return Array.from(lines, ([y, values]) => ({ y, values }));
  }

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawLines(
    data: TwoWayLineData,
    ctx: CanvasRenderingContext2D,
    line: Line<Point>,
    color: ScaleSequential<string> | ScaleOrdinal<number, string>
  ) {
    // TODO: is this check needed?
    if (
      ctx === null ||
      ctx === undefined ||
      line === null ||
      line === undefined
    ) {
      return;
    }
    ctx.save();

    ctx.clearRect(0, 0, width, height);

    // normal ice lines

    ctx.lineWidth = 1;
    ctx.globalAlpha = 1;

    data.forEach(({ y, values }) => {
      ctx.strokeStyle = color(y);
      ctx.beginPath();
      line(values);
      ctx.stroke();
    });

    ctx.restore();
  }

  /*
  If scaleCanvas is called after drawHeatmap, then it will clear the canvas.
  This was happening when changing the sorting order of the PDPs.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pd, x, y, color, or showInteractions.
  */
  function draw() {
    // TODO: are these checks needed?
    if (
      ctx &&
      x !== null &&
      x !== undefined &&
      y !== null &&
      y !== undefined &&
      line !== null &&
      line !== undefined
    ) {
      drawLines(data, ctx, line, color);
    }
  }
  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, heightExcludingLegend);
    draw();
  }

  $: if (
    ctx &&
    x !== null &&
    x !== undefined &&
    y !== null &&
    y !== undefined &&
    line !== null &&
    line !== undefined
  ) {
    drawLines(data, ctx, line, color);
  }
</script>

<div class="two-way-container" style:--top={legendHeight}>
  {#if showColorLegend}
    <div style:margin-left="{margin.left}px">
      {#if 'interpolator' in color}
        <QuantitativeColorLegend
          width={width - margin.left - margin.right}
          height={legendHeight}
          {color}
          title={pd.y_feature}
          marginLeft={10}
          marginRight={10}
        />
      {:else}
        <CategoricalColorLegend
          width={width - margin.left - margin.right}
          height={legendHeight}
          {color}
          value_map={'value_map' in yFeature ? yFeature.value_map : {}}
          title={pd.y_feature}
          marginLeft={10}
          marginRight={10}
        />
      {/if}
    </div>
  {/if}

  <canvas bind:this={canvas} />

  <svg {width} height={heightExcludingLegend}>
    <XAxis
      scale={x}
      y={heightExcludingLegend - margin.bottom}
      label={pd.x_feature}
      integerOnly={xFeature.subkind === 'discrete'}
      value_map={'value_map' in xFeature ? xFeature.value_map : {}}
    />

    <YAxis
      scale={y}
      x={margin.left}
      label={'prediction'}
      integerOnly={yFeature.subkind === 'discrete'}
      value_map={'value_map' in yFeature ? yFeature.value_map : {}}
    />
  </svg>
</div>

<style>
  .two-way-container {
    position: relative;
    width: 100%;
    height: 100%;
  }

  svg,
  canvas {
    position: absolute;
    top: var(--top);
    left: 0;
  }
</style>
