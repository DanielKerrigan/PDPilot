<script lang="ts">
  import type { OneWayPD } from '../../../types';
  import { range } from 'd3-array';
  import { scaleLinear, scaleOrdinal, scalePoint, scaleBand } from 'd3-scale';
  import type { ScaleBand } from 'd3-scale';
  import type { Line } from 'd3-shape';
  import { line as d3line } from 'd3-shape';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    centered_ice_line_extent,
    feature_info,
    one_way_pds,
    detailedFeature1,
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
  // marginTop is space above all plots / beneath header
  export let marginTop: number;
  export let marginalPlotHeight: number;
  export let showTitle: boolean;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  $: feature = $feature_info[pd.x_feature];

  // margin.top is space above each individual plot
  const margin = {
    top: 5,
    right: 10,
    bottom: 35,
    left: 50,
  };

  let borderBoxSize: ResizeObserverSize[] | undefined | null;

  $: chartHeight =
    (borderBoxSize ? borderBoxSize[0].blockSize : height) - marginTop;

  $: clusterIds = range(pd.ice.num_clusters);

  $: clusters = pd.ice.clusters[pd.ice.num_clusters].clusters;

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
    $centered_ice_line_extent,
    margin
  );

  $: dark = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.dark);

  $: light = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.light);

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

    clusters.forEach((cluster) => {
      ctx.translate(0, fy(cluster.id) ?? 0);

      // cluster ice lines

      ctx.lineWidth = 1.0;
      ctx.strokeStyle = light(cluster.id);
      ctx.globalAlpha = 0.25;

      cluster.indices.forEach((idx) => {
        if (indices === null || indices.includes(idx)) {
          ctx.beginPath();
          line(pd.ice.centered_ice_lines[idx]);
          ctx.stroke();
        }
      });

      // pdp line

      ctx.lineWidth = 1.0;
      ctx.strokeStyle = 'black';
      ctx.globalAlpha = 1.0;

      ctx.beginPath();
      line(pd.ice.centered_pdp);
      ctx.stroke();

      // cluster mean line

      ctx.lineWidth = 2.0;
      ctx.strokeStyle = dark(cluster.id);
      ctx.globalAlpha = 1.0;

      ctx.beginPath();
      line(cluster.centered_mean);
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

  function setNumClusters(numClusters: number) {
    if (numClusters < 2 || numClusters > 5) {
      return;
    }

    Object.assign(pd.ice, { num_clusters: numClusters });
    $one_way_pds = $one_way_pds;
    // this causes the detailed plot to update
    // TODO: find a better way to do this
    $detailedFeature1 = '';
    $detailedFeature1 = pd.x_feature;

    // update the extent for ICE cluster centers

    let clusterCenterMin = Infinity;
    let clusterCenterMax = -Infinity;

    for (const owp of $one_way_pds) {
      const clusters = owp.ice.clusters;
      const n = owp.ice.num_clusters;

      if (n in clusters) {
        const cluster = clusters[n];

        if (cluster.centered_mean_min < clusterCenterMin) {
          clusterCenterMin = cluster.centered_mean_min;
        }

        if (cluster.centered_mean_max > clusterCenterMax) {
          clusterCenterMax = cluster.centered_mean_max;
        }
      }
    }

    $ice_cluster_center_extent = [clusterCenterMin, clusterCenterMax];
  }
</script>

<div class="cluster-lines-container">
  <div class="cluster-lines-header">
    {#if showTitle}
      <div class="cluster-lines-title pdpilot-bold">ICE Clusters</div>
    {/if}
    <div class="cluster-lines-settings">
      <div>Number of clusters:</div>
      <div class="num-cluster-change">
        <button
          disabled={pd.ice.num_clusters <= 2}
          on:click={() => setNumClusters(pd.ice.num_clusters - 1)}
          title="Decrement number of clusters"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="pdpilot-icon icon-tabler icon-tabler-minus"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path d="M5 12l14 0" />
          </svg>
        </button>

        <div class="current-num-clusters">{pd.ice.num_clusters}</div>

        <button
          disabled={pd.ice.num_clusters === 1 || pd.ice.num_clusters >= 5}
          on:click={() => setNumClusters(pd.ice.num_clusters + 1)}
          title="Increment number of clusters"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="pdpilot-icon icon-tabler icon-tabler-plus"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path d="M12 5l0 14" />
            <path d="M5 12l14 0" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  {#if showMarginalDistribution}
    <svg {width} height={marginTop}>
      {#if 'bandwidth' in x}
        <MarginalBarChart
          data={$feature_info[pd.x_feature].distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[0, marginTop - marginalPlotHeight]}
        />
      {:else}
        <MarginalHistogram
          data={$feature_info[pd.x_feature].distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[0, marginTop - marginalPlotHeight]}
        />
      {/if}
    </svg>
  {/if}
  <div
    class="cluster-lines-chart"
    style:margin-top="{showMarginalDistribution ? 0 : marginTop}px"
    bind:borderBoxSize
  >
    <canvas bind:this={canvas} />
    <svg class="svg-for-clusters" height={chartHeight} {width}>
      {#each clusters as cluster}
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
</div>

<style>
  .cluster-lines-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .cluster-lines-header {
    margin-bottom: 0.5em;
  }

  .cluster-lines-settings {
    display: flex;
    align-items: center;
    gap: 0.5em;
  }

  .cluster-lines-chart {
    position: relative;
    width: 100%;
    flex: 1;
  }

  .num-cluster-change {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .svg-for-clusters,
  canvas {
    position: absolute;
    top: 0;
    left: 0;
  }
</style>
