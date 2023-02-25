<script lang="ts">
  import type { OneWayPD } from '../../../types';
  import { scaleLinear, scaleOrdinal, scalePoint, scaleBand } from 'd3-scale';
  import type { ScaleBand } from 'd3-scale';
  import type { Line } from 'd3-shape';
  import { line as d3line } from 'd3-shape';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    ice_cluster_band_extent,
    ice_cluster_line_extent,
    feature_info,
  } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import {
    categoricalColors,
    getYScale,
    scaleCanvas,
  } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import { onMount } from 'svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  export let indices: number[] | null;
  export let marginTop: number;
  export let distributionHeight: number;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: feature = $feature_info[pd.x_feature];

  // TODO: better handle marginTop vs. margin.top
  $: margin = {
    top: 5,
    right: 10,
    bottom: 35,
    left: 50,
  };

  $: chartHeight = height - marginTop;

  $: clusterIds = pd.ice.clusters.map((d) => d.id);

  $: fy = scaleBand<number>().domain(clusterIds).range([0, chartHeight]);

  $: facetHeight = fy.bandwidth();

  $: x =
    feature.kind === 'quantitative'
      ? scaleLinear()
          .domain([pd.x_values[0], pd.x_values[pd.x_values.length - 1]])
          .range([margin.left, width - margin.right])
      : scalePoint<number>()
          .domain(pd.x_values)
          .range([margin.left, width - margin.right])
          .padding(0.5);

  $: y = getYScale(
    pd,
    chartHeight,
    facetHeight,
    'cluster-lines',
    scaleLocally,
    $ice_line_extent,
    $ice_cluster_center_extent,
    $ice_cluster_band_extent,
    $ice_cluster_line_extent,
    margin
  );

  $: dark = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.dark);

  $: medium = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: line = d3line<number>()
    .x((_, i) => x(pd.x_values[i]) ?? 0)
    .y((d) => y(d))
    .context(ctx);

  // canvas

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawIcePdp(
    pd: OneWayPD,
    ctx: CanvasRenderingContext2D,
    line: Line<number>,
    indices: number[] | null,
    fy: ScaleBand<number>,
    width: number,
    height: number
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

    pd.ice.clusters.forEach((cluster) => {
      ctx.translate(0, fy(cluster.id) ?? 0);

      // cluster ice lines

      ctx.lineWidth = 1.0;
      ctx.strokeStyle = medium(cluster.id);
      ctx.globalAlpha = 0.25;

      cluster.centered_ice_lines.forEach((d, i) => {
        if (indices === null || indices.includes(cluster.indices[i])) {
          ctx.beginPath();
          line(d);
          ctx.stroke();
        }
      });

      // cluster mean line

      ctx.lineWidth = 2.0;
      ctx.strokeStyle = dark(cluster.id);
      ctx.globalAlpha = 1.0;

      ctx.beginPath();
      line(cluster.centered_mean);
      ctx.stroke();

      // pdp line

      ctx.lineWidth = 2.0;
      ctx.strokeStyle = 'black';
      ctx.globalAlpha = 1.0;

      ctx.beginPath();
      line(pd.ice.centered_pdp);
      ctx.stroke();

      // undo translate
      ctx.translate(0, -(fy(cluster.id) ?? 0));
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
    drawIcePdp(pd, ctx, line, indices, fy, width, chartHeight);
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, chartHeight);
    draw();
  }

  $: drawIcePdp(pd, ctx, line, indices, fy, width, chartHeight);
</script>

{#if showMarginalDistribution}
  <svg {width} height={marginTop}>
    {#if 'bandwidth' in x}
      <MarginalBarChart
        data={$feature_info[pd.x_feature].distribution}
        {x}
        height={distributionHeight}
        direction="horizontal"
        translate={[0, marginTop - distributionHeight]}
      />
    {:else}
      <MarginalHistogram
        data={$feature_info[pd.x_feature].distribution}
        {x}
        height={distributionHeight}
        direction="horizontal"
        translate={[0, marginTop - distributionHeight]}
      />
    {/if}
  </svg>
{/if}

<div>
  <canvas bind:this={canvas} />

  <svg class="svg-for-clusters" height={chartHeight} {width}>
    {#each pd.ice.clusters as cluster}
      <g transform="translate(0,{fy(cluster.id) ?? 0})">
        <YAxis scale={y} x={margin.left} label={'centered prediction'} />
        <XAxis
          scale={x}
          y={facetHeight - margin.bottom}
          showTickLabels={cluster.id === clusterIds[clusterIds.length - 1]}
          showAxisLabel={cluster.id === clusterIds[clusterIds.length - 1]}
          label={pd.x_feature}
          integerOnly={feature.subkind === 'discrete'}
          value_map={'value_map' in feature ? feature.value_map : {}}
        />
      </g>
    {/each}
  </svg>
</div>

<style>
  div {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .svg-for-clusters,
  canvas {
    position: absolute;
    top: 0;
    left: 0;
  }
</style>
