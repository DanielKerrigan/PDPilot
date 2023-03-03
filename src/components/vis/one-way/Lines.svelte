<script lang="ts">
  import type { Distribution, OneWayPD } from '../../../types';
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
    brushingInProgress,
    highlightedDistributions,
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
  export let showMarginalDistribution: boolean;
  export let marginTop: number;
  export let distributionHeight: number;
  export let allowBrushing = false;
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
    center ? 'centered-lines' : 'lines',
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

  $: showHighlights = allowBrushing && $highlighted_indices.length > 0;

  // canvas

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawIcePdp(
    pd: OneWayPD,
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

    const iceLines = center ? pd.ice.centered_ice_lines : pd.ice.ice_lines;

    iceLines.forEach((d) => {
      ctx.beginPath();
      line(d);
      ctx.stroke();
    });

    // highlighted ice lines

    if (showHighlights) {
      ctx.strokeStyle = 'red';
      ctx.globalAlpha = 0.15;

      highlight.forEach((i) => {
        ctx.beginPath();
        line(iceLines[i]);
        ctx.stroke();
      });
    }

    // pdp line

    ctx.lineWidth = 2;
    ctx.strokeStyle = 'black';
    ctx.globalAlpha = 1;

    ctx.beginPath();
    line(center ? pd.ice.centered_pdp : pd.mean_predictions);
    ctx.stroke();

    // pdp circles

    if ('step' in x) {
      for (let i = 0; i < pd.x_values.length; i++) {
        const cx = x(pd.x_values[i]) ?? 0;
        const cy = y(center ? pd.ice.centered_pdp[i] : pd.mean_predictions[i]);

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
      pd,
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
    pd,
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

    // get the left and right x pixel coordinates of the brush
    const [[x1, y1], [x2, y2]] = selection as [
      [number, number],
      [number, number]
    ];

    const xs = pd.x_values.map((v) => x(v) ?? 0);

    const iceLines = center ? pd.ice.centered_ice_lines : pd.ice.ice_lines;

    $highlighted_indices = iceLines
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

  function brushEnd(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection === null) {
      activeBrush = false;
      $highlighted_indices = [];
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

  function getMaxPercent(
    overall: Distribution,
    highlighted: Distribution | undefined
  ) {
    const maxOverall = Math.max(...overall.percents);

    if (!highlighted) {
      return maxOverall;
    }

    const maxHighlighted = Math.max(...highlighted.percents);

    return Math.max(maxOverall, maxHighlighted);
  }

  $: maxPercent = getMaxPercent(feature.distribution, highlightedDistribution);
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

      <YAxis
        scale={y}
        x={margin.left}
        label={center ? 'centered prediction' : 'prediction'}
      />

      {#if showMarginalDistribution}
        {#if allowBrushing && highlightedDistribution && $highlighted_indices.length > 0}
          {#if 'bandwidth' in x}
            <MarginalBarChart
              data={highlightedDistribution}
              fill={'var(--light-red)'}
              {x}
              height={distributionHeight}
              direction="horizontal"
              translate={[0, margin.top - distributionHeight]}
              unit={'percent'}
              maxValue={maxPercent}
            />
          {:else}
            <MarginalHistogram
              data={highlightedDistribution}
              fill={'var(--light-red)'}
              {x}
              height={distributionHeight}
              direction="horizontal"
              translate={[0, margin.top - distributionHeight]}
              unit={'percent'}
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
            height={distributionHeight}
            direction="horizontal"
            translate={[0, margin.top - distributionHeight]}
            unit={'percent'}
            maxValue={maxPercent}
          />
        {:else}
          <MarginalHistogram
            data={feature.distribution}
            fill={showHighlightedDistribution ? 'none' : 'var(--gray-3)'}
            stroke={showHighlightedDistribution ? 'var(--black)' : 'none'}
            {x}
            height={distributionHeight}
            direction="horizontal"
            translate={[0, margin.top - distributionHeight]}
            unit={'percent'}
            maxValue={maxPercent}
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
    top: 0;
    left: 0;
  }
</style>
