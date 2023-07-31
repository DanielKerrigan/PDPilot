<script lang="ts">
  import type { Distribution, OneWayPD } from '../../../types';
  import { centerIceLines } from '../../../utils';
  import { scaleLinear, scalePoint } from 'd3-scale';
  import type { ScaleLinear, ScalePoint } from 'd3-scale';
  import { line as d3line } from 'd3-shape';
  import type { Line } from 'd3-shape';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    centered_ice_line_extent,
    feature_info,
    highlighted_indices,
    brushingInProgress,
    highlightedDistributions,
    brushedFeature,
    feature_to_ice_lines,
  } from '../../../stores';
  import { select } from 'd3-selection';
  import type { Selection } from 'd3-selection';
  import type { D3BrushEvent } from 'd3-brush';
  import { brush as d3brush } from 'd3-brush';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import {
    getMaxPercent,
    getYScale,
    highlightColor,
    scaleCanvas,
  } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { onMount } from 'svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let marginTop: number;
  export let marginalPlotHeight: number;
  export let allowBrushing = false;
  export let showBrushedBorder = false;
  export let iceLineWidth: number;
  export let center = false;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: feature = $feature_info[pd.x_feature];

  $: margin = {
    top: marginTop,
    right: 10,
    bottom: 35,
    left: 50,
  };

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
    height,
    0,
    center ? 'centered-lines' : 'lines',
    scaleLocally,
    $ice_line_extent,
    $ice_cluster_center_extent,
    $centered_ice_line_extent,
    margin
  );

  // this approach with the indices is like what is done here
  // https://observablehq.com/@d3/line-chart

  $: line = d3line<number>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y((d) => y(d))
    .context(ctx);

  $: showHighlights = allowBrushing && $highlighted_indices.length > 0;

  $: standardIceLines = $feature_to_ice_lines[pd.x_feature];
  $: centeredIceLines = centerIceLines(standardIceLines);

  $: iceLines = center ? centeredIceLines : standardIceLines;
  $: pdpLine = center ? pd.ice.centered_pdp : pd.mean_predictions;

  // canvas

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawIcePdp(
    iceLines: number[][],
    pdpLine: number[],
    xValues: number[],
    ctx: CanvasRenderingContext2D,
    line: Line<number>,
    highlight: number[],
    x: ScaleLinear<number, number, never> | ScalePoint<number>,
    y: ScaleLinear<number, number, never>,
    iceLineWidth: number,
    radius: number,
    showHighlights: boolean,
    width: number,
    height: number,
    center: boolean
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

    ctx.lineWidth = iceLineWidth;
    // same as css var(--gray-2)
    ctx.strokeStyle = 'rgb(198, 198, 198)';
    ctx.globalAlpha = 0.15;

    iceLines.forEach((d) => {
      ctx.beginPath();
      line(d);
      ctx.stroke();
    });

    // highlighted ice lines

    if (showHighlights) {
      ctx.strokeStyle = highlightColor;
      ctx.globalAlpha = 0.3;

      highlight.forEach((i) => {
        ctx.beginPath();
        line(iceLines[i]);
        ctx.stroke();
      });
    }

    // pdp line

    ctx.lineWidth = 2;
    ctx.strokeStyle = 'black';
    ctx.fillStyle = 'black';
    ctx.globalAlpha = 1;

    ctx.beginPath();
    line(pdpLine);
    ctx.stroke();

    // pdp circles

    if ('step' in x) {
      for (let i = 0; i < xValues.length; i++) {
        const cx = x(xValues[i]) ?? 0;
        const cy = y(pdpLine[i]);

        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    ctx.restore();
  }

  /*
  TODO: is this true in this case?
  If scaleCanvas is called after drawLines, then it will clear the canvas.
  We need the draw function so that the reactive statement for scaleCanvas is
  not dependent on pd or line.
  */
  function draw() {
    drawIcePdp(
      iceLines,
      pdpLine,
      pd.x_values,
      ctx,
      line,
      $highlighted_indices,
      x,
      y,
      iceLineWidth,
      radius,
      showHighlights,
      width,
      height,
      center
    );
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, height);
    draw();
  }

  $: drawIcePdp(
    iceLines,
    pdpLine,
    pd.x_values,
    ctx,
    line,
    $highlighted_indices,
    x,
    y,
    iceLineWidth,
    radius,
    showHighlights,
    width,
    height,
    center
  );

  // brushing

  // does the brush for this feature have a selection
  // TODO: can we get rid of this and just use $brushedFeature?
  let activeBrush = false;
  // is the brush for this feature being moved
  let brushingThisFeatureInProgress = false;

  function brushStart(this: SVGGElement, _: D3BrushEvent<undefined>) {
    activeBrush = true;
    $brushingInProgress = true;
    brushingThisFeatureInProgress = true;
  }

  // guided by https://observablehq.com/@d3/brushable-parallel-coordinates
  // and https://observablehq.com/@d3/brushable-scatterplot-matrix
  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (!selection) {
      $highlighted_indices = [];
      return;
    }

    $brushedFeature = pd.x_feature;

    // get the left and right x pixel coordinates of the brush
    const [[x1, y1], [x2, y2]] = selection as [
      [number, number],
      [number, number]
    ];

    // pixel coordinates of the x values
    const xs = pd.x_values.map((v) => x(v) ?? 0);

    $highlighted_indices = iceLines
      .map((lines, index) => ({ lines, index }))
      .filter(({ lines }) => {
        return lines.some((point, i) => {
          const yy = y(point);
          const xx = xs[i];

          return xx >= x1 && xx <= x2 && yy >= y1 && yy <= y2;
        });
      })
      .map(({ index }) => index);
  }

  function brushEnd(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection === null) {
      activeBrush = false;
      $highlighted_indices = [];
      $brushedFeature = '';
    }

    $brushingInProgress = false;
    brushingThisFeatureInProgress = false;
    // TODO: make selection on a plot.
    // start a selection on another plot.
    // original plot stays highlight until moving. why?
  }

  $: brush = d3brush<undefined>()
    .extent([
      [margin.left, margin.top],
      [width - margin.right, height - margin.bottom],
    ])
    .on('start', brushStart)
    .on('brush', brushed)
    .on('end', brushEnd);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, null, undefined>;

  // TODO: this won't disable brushing after it's enabled
  $: if (group && allowBrushing) {
    selection = select(group);
    selection.call(brush);
  }

  // clear this brush if another feature is being brushed
  $: if ($brushingInProgress && activeBrush && !brushingThisFeatureInProgress) {
    selection.call(brush.clear);
  }

  let highlightedDistribution: Distribution | undefined;
  $: highlightedDistribution = $highlightedDistributions.get(pd.x_feature);

  $: showHighlightedDistribution =
    allowBrushing && highlightedDistribution && $highlighted_indices.length > 0;

  $: maxPercent = getMaxPercent(feature.distribution, highlightedDistribution);
</script>

<div class="pdpilot-plot-container">
  <canvas bind:this={canvas} />

  <svg {width} {height}>
    <g bind:this={group}>
      <XAxis
        scale={x}
        y={height - margin.bottom}
        label={pd.x_feature}
        integerOnly={feature.subkind === 'discrete'}
        value_map={'value_map' in feature ? feature.value_map : {}}
      />

      <YAxis
        scale={y}
        x={margin.left}
        label={center ? 'Centered prediction' : 'Prediction'}
      />

      {#if showMarginalDistribution}
        {#if allowBrushing && highlightedDistribution && $highlighted_indices.length > 0}
          {#if 'bandwidth' in x}
            <MarginalBarChart
              data={highlightedDistribution}
              fill={highlightColor}
              {x}
              height={marginalPlotHeight}
              direction="horizontal"
              translate={[0, margin.top - marginalPlotHeight]}
              unit="percent"
              maxValue={maxPercent}
            />
          {:else}
            <MarginalHistogram
              data={highlightedDistribution}
              fill={highlightColor}
              {x}
              height={marginalPlotHeight}
              direction="horizontal"
              translate={[0, margin.top - marginalPlotHeight]}
              unit="percent"
              maxValue={maxPercent}
            />
          {/if}
        {/if}
        {#if 'bandwidth' in x}
          <MarginalBarChart
            data={feature.distribution}
            fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
            stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
            {x}
            height={marginalPlotHeight}
            direction="horizontal"
            translate={[0, margin.top - marginalPlotHeight]}
            unit="percent"
            maxValue={maxPercent}
          />
        {:else}
          <MarginalHistogram
            data={feature.distribution}
            fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
            stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
            {x}
            height={marginalPlotHeight}
            direction="horizontal"
            translate={[0, margin.top - marginalPlotHeight]}
            unit="percent"
            maxValue={maxPercent}
          />
        {/if}
      {/if}

      <!-- border around brushed plot -->
      {#if showBrushedBorder && $brushedFeature === pd.x_feature}
        <rect
          x={margin.left}
          y={margin.top}
          width={width - margin.left - margin.right}
          height={height - margin.top - margin.bottom}
          stroke="var(--gray-2)"
          fill="none"
          pointer-events="none"
        />
      {/if}
    </g>
  </svg>
</div>

<style>
  .pdpilot-plot-container {
    width: 100%;
    height: 100%;
    position: relative;
  }

  svg,
  canvas {
    position: absolute;
    top: 0;
    left: 0;
  }
</style>
