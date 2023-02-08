<script lang="ts">
  import type { MarginalDistributionKind, OneWayPD } from '../../../types';
  import { scaleLinear, scalePoint } from 'd3-scale';
  import type { ScaleLinear, ScalePoint } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import type { Line } from 'd3-shape';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    ice_cluster_band_extent,
    ice_cluster_line_extent,
    feature_info,
    highlighted_indices,
    dataset,
  } from '../../../stores';
  import { select } from 'd3-selection';
  import type { Selection } from 'd3-selection';
  import type { D3BrushEvent } from 'd3-brush';
  import { brush as d3brush } from 'd3-brush';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import { getYScale, scaleCanvas } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { onMount } from 'svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let marginalDistributionKind: MarginalDistributionKind;
  export let marginTop: number;
  export let marginRight: number;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: feature = $feature_info[pd.x_feature];
  $: values = $dataset[pd.x_feature];
  $: highlightedValues = $highlighted_indices.map((i) => values[i]);

  $: margin = {
    top: marginTop,
    right: marginRight,
    bottom: 35,
    left: 50,
  };

  $: chartHeight = height;
  $: facetHeight = chartHeight / pd.ice.clusters.length;

  $: x =
    feature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_values[0], pd.x_values[pd.x_values.length - 1]])
          .range([margin.left, width - margin.right])
      : scalePoint<number>()
          .domain(pd.x_values)
          .range([margin.left, width - margin.right])
          .padding(0.5);

  $: radius = 'step' in x ? Math.min(3, x.step() / 2 - 1) : 0;

  $: y = getYScale(
    pd,
    chartHeight,
    facetHeight,
    'lines',
    scaleLocally,
    $ice_line_extent,
    $ice_cluster_center_extent,
    $ice_cluster_band_extent,
    $ice_cluster_line_extent,
    margin
  );

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: line = d3line<number>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y((d) => y(d))
    .context(ctx);

  // canvas

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawIcePdp(
    data: OneWayPD,
    ctx: CanvasRenderingContext2D,
    line: Line<number>,
    highlight: number[],
    x: ScaleLinear<number, number, never> | ScalePoint<number>,
    y: ScaleLinear<number, number, never>,
    pd: OneWayPD,
    radius: number
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

    ctx.lineWidth = 0.5;
    // same as css var(--gray-2)
    ctx.strokeStyle = 'rgb(198, 198, 198)';
    ctx.globalAlpha = 0.15;

    data.ice.ice_lines.forEach((d) => {
      ctx.beginPath();
      line(d);
      ctx.stroke();
    });

    // highlighted ice lines

    ctx.strokeStyle = 'red';
    ctx.globalAlpha = 0.15;

    highlight.forEach((i) => {
      ctx.beginPath();
      line(data.ice.ice_lines[i]);
      ctx.stroke();
    });

    // pdp line

    ctx.lineWidth = 2;
    ctx.strokeStyle = 'black';
    ctx.globalAlpha = 1;

    ctx.beginPath();
    line(data.mean_predictions);
    ctx.stroke();

    // pdp circles

    if ('step' in x) {
      for (let i = 0; i < pd.x_values.length; i++) {
        const cx = x(pd.x_values[i]) ?? 0;
        const cy = y(pd.mean_predictions[i]);

        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    ctx.restore();
  }

  function drawMarginalStripPlot(
    values: number[],
    highlightedValues: number[],
    ctx: CanvasRenderingContext2D,
    x: ScaleLinear<number, number, never> | ScalePoint<number>
  ) {
    if (ctx === null || ctx === undefined) {
      return;
    }

    ctx.save();

    ctx.clearRect(0, 0, width, margin.top);

    ctx.lineWidth = 0.5;
    // same as css var(--gray-2)
    ctx.strokeStyle = 'rgb(198, 198, 198)';
    ctx.globalAlpha = 0.15;

    values.forEach((v) => {
      ctx.beginPath();
      ctx.moveTo(x(v) ?? 0, 0);
      ctx.lineTo(x(v) ?? 0, margin.top);
      ctx.stroke();
    });

    ctx.strokeStyle = 'red';

    highlightedValues.forEach((v) => {
      ctx.beginPath();
      ctx.moveTo(x(v) ?? 0, 0);
      ctx.lineTo(x(v) ?? 0, margin.top);
      ctx.stroke();
    });

    ctx.restore();
  }

  /*
  TODO: is this true in this case?
  If scaleCanvas is called after drawLines, then it will clear the canvas.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pd or line.
  */
  function draw() {
    drawIcePdp(pd, ctx, line, $highlighted_indices, x, y, pd, radius);
    if (marginalDistributionKind === 'strip') {
      drawMarginalStripPlot(values, highlightedValues, ctx, x);
    }
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, height);
    draw();
  }

  $: drawIcePdp(pd, ctx, line, $highlighted_indices, x, y, pd, radius);
  $: if (marginalDistributionKind === 'strip') {
    drawMarginalStripPlot(values, highlightedValues, ctx, x);
  }

  // brushing

  // guided by https://observablehq.com/@d3/brushable-parallel-coordinates
  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection === null) {
      $highlighted_indices = [];
    } else {
      // get the left and right x pixel coordinates of the brush
      const [[x1, y1], [x2, y2]] = selection as [
        [number, number],
        [number, number]
      ];

      const xs = pd.x_values.map((v) => x(v) ?? 0);

      $highlighted_indices = pd.ice.ice_lines
        .map((il, i) => ({ lines: il, index: i }))
        .filter(({ lines }) => {
          return lines.some((point, i) => {
            const yy = y(point);
            const xx = xs[i];

            return xx >= x1 && xx <= x2 && yy >= y1 && yy <= y2;
          });
        })
        .map(({ index }) => index);
    }
  }

  $: brush = d3brush<undefined>()
    .extent([
      [margin.left, margin.top],
      [width - margin.right, height - margin.bottom],
    ])
    .on('start brush end', brushed);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, null, undefined>;

  $: if (group) {
    selection = select(group);
    selection.call(brush);
  }
</script>

<div>
  <canvas bind:this={canvas} />

  <svg {width} {height}>
    <g bind:this={group}>
      <XAxis
        scale={x}
        y={chartHeight - margin.bottom}
        label={pd.x_feature}
        integerOnly={feature.subkind === 'discrete'}
        value_map={'value_map' in feature ? feature.value_map : {}}
      />

      <YAxis scale={y} x={margin.left} label={'prediction'} />

      {#if marginalDistributionKind === 'bars'}
        {#if 'bandwidth' in x}
          <MarginalBarChart
            data={$feature_info[pd.x_feature].distribution}
            {x}
            height={margin.top}
            direction="horizontal"
            {highlightedValues}
          />
        {:else}
          <MarginalHistogram
            data={$feature_info[pd.x_feature].distribution}
            {x}
            height={margin.top}
            direction="horizontal"
            {highlightedValues}
          />
        {/if}
      {/if}
    </g>
  </svg>
</div>

<style>
  div {
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
