<script lang="ts">
  import type { OneWayPD } from '../../../types';
  import { range } from 'd3-array';
  import { scaleLinear, scaleOrdinal, scalePoint, scaleBand } from 'd3-scale';
  import type { ScaleBand } from 'd3-scale';
  import type { Line } from 'd3-shape';
  import { line as d3line } from 'd3-shape';
  import type { D3BrushEvent } from 'd3-brush';
  import { brush as d3brush } from 'd3-brush';
  import { select } from 'd3-selection';
  import type { Selection } from 'd3-selection';
  import XAxis from '../axis/XAxis.svelte';
  import YAxis from '../axis/YAxis.svelte';
  import {
    ice_line_extent,
    ice_cluster_center_extent,
    centered_ice_line_extent,
    feature_info,
    one_way_pds,
    cluster_update,
  } from '../../../stores';
  import MarginalHistogram from '../marginal/MarginalHistogram.svelte';
  import {
    categoricalColors,
    getYScale,
    scaleCanvas,
  } from '../../../vis-utils';
  import MarginalBarChart from '../marginal/MarginalBarChart.svelte';
  import cloneDeep from 'lodash.clonedeep';
  import { onMount, tick } from 'svelte';
  import { getClustering } from '../../../utils';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let scaleLocally: boolean;
  export let showMarginalDistribution: boolean;
  // TODO: make this a set
  export let indices: number[] | null;
  // marginTop is space above all plots / beneath header
  export let marginTop: number;
  export let marginalPlotHeight: number;
  export let showTitle: boolean;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  // we need to modify the PD when the number of clusters is changed
  // doing this in place leads to backbone not syncing with python.
  $: copyPd = cloneDeep(pd);
  $: feature = $feature_info[copyPd.x_feature];

  $: featureIndex = $one_way_pds.findIndex(
    (d) => d.x_feature === copyPd.x_feature
  );

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

  $: clusterIds = range(copyPd.ice.num_clusters);

  $: clusters = getClustering(copyPd).clusters;

  $: isAdjusted = copyPd.ice.num_clusters in copyPd.ice.adjusted_clusterings;

  $: allLinesInClustedBrushed =
    sourceClusterId !== -1 &&
    clusters[sourceClusterId].indices.length === brushedIndices.size;

  $: fy = scaleBand<number>().domain(clusterIds).range([0, chartHeight]);

  $: facetHeight = fy.bandwidth();

  $: x =
    feature.kind === 'quantitative'
      ? scaleLinear()
          .domain([
            copyPd.x_values[0],
            copyPd.x_values[copyPd.x_values.length - 1],
          ])
          .range([margin.left, width - margin.right])
      : scalePoint<number>()
          .domain(copyPd.x_values)
          .range([margin.left, width - margin.right])
          .padding(0.5);

  $: y = getYScale(
    copyPd,
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

  $: medium = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: light = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.light);

  $: line = d3line<number>()
    .x((_, i) => x(copyPd.x_values[i]) ?? 0)
    .y((d) => y(d))
    .context(ctx);

  // canvas

  onMount(() => {
    ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  });

  function drawClusterLines(
    pd: OneWayPD,
    ctx: CanvasRenderingContext2D,
    line: Line<number>,
    indices: number[] | null,
    fy: ScaleBand<number>,
    width: number,
    height: number,
    brushedIndices: Set<number>,
    sourceClusterId: number
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
      ctx.globalAlpha = 0.25;

      cluster.indices.forEach((idx) => {
        if (indices === null || indices.includes(idx)) {
          ctx.beginPath();
          ctx.strokeStyle =
            cluster.id === sourceClusterId && !brushedIndices.has(idx)
              ? 'rgb(171, 171, 171)'
              : light(cluster.id);
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
    drawClusterLines(
      copyPd,
      ctx,
      line,
      indices,
      fy,
      width,
      chartHeight,
      brushedIndices,
      sourceClusterId
    );
  }

  $: if (ctx) {
    scaleCanvas(canvas, ctx, width, chartHeight);
    draw();
  }

  $: drawClusterLines(
    copyPd,
    ctx,
    line,
    indices,
    fy,
    width,
    chartHeight,
    brushedIndices,
    sourceClusterId
  );

  function setNumClusters(numClusters: number) {
    if (numClusters < 2 || numClusters > 5) {
      return;
    }

    // don't mutate $one_way_pds directly
    // TOOD: is the Object.assign needed here?
    Object.assign(copyPd.ice, { num_clusters: numClusters });
    const one_ways = Array.from($one_way_pds);
    one_ways[featureIndex] = copyPd;
    $one_way_pds = one_ways;

    // update the extent for ICE cluster centers

    let clusterCenterMin = Infinity;
    let clusterCenterMax = -Infinity;

    for (const owp of $one_way_pds) {
      const n = owp.ice.num_clusters;

      if (n !== 1) {
        const clustering = getClustering(owp, n);

        if (clustering.centered_mean_min < clusterCenterMin) {
          clusterCenterMin = clustering.centered_mean_min;
        }

        if (clustering.centered_mean_max > clusterCenterMax) {
          clusterCenterMax = clustering.centered_mean_max;
        }
      }
    }

    $ice_cluster_center_extent = [clusterCenterMin, clusterCenterMax];
  }

  // brushing and modifying clusters

  let brushedIndices: Set<number> = new Set();
  let sourceClusterId = -1;
  let brushedGroupSelection: Selection<
    SVGGElement,
    undefined,
    null,
    undefined
  > | null = null;

  function brushStart(this: SVGGElement, _: D3BrushEvent<undefined>) {
    if (brushedGroupSelection && brushedGroupSelection.node() !== this) {
      brushedGroupSelection.call(brush.clear);
    }

    sourceClusterId = +this.id.split('-')[1];
    brushedGroupSelection = select(this);
  }

  // guided by https://observablehq.com/@d3/brushable-parallel-coordinates
  // and https://observablehq.com/@d3/brushable-scatterplot-matrix
  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (!selection) {
      brushedIndices = new Set();
      return;
    }

    // get the left and right x pixel coordinates of the brush
    const [[x1, y1], [x2, y2]] = selection as [
      [number, number],
      [number, number]
    ];

    const cluster = clusters.find((c) => c.id === sourceClusterId);

    if (!cluster) {
      return;
    }

    // pixel coordinates of the x values
    const xs = copyPd.x_values.map((v) => x(v) ?? 0);

    const iceLines = cluster.indices
      .filter((i) => indices === null || indices.includes(i))
      .map((i) => ({
        line: copyPd.ice.centered_ice_lines[i],
        index: i,
      }));

    brushedIndices = new Set(
      iceLines
        .filter(({ line }) => {
          return line.some((point, i) => {
            const yy = y(point);
            const xx = xs[i];

            return xx >= x1 && xx <= x2 && yy >= y1 && yy <= y2;
          });
        })
        .map(({ index }) => index)
    );
  }

  function brushEnd(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection === null) {
      brushedIndices = new Set();
      sourceClusterId = -1;
    }
  }

  $: brush = d3brush<undefined>()
    .extent([
      [margin.left, margin.top],
      [width - margin.right, facetHeight - margin.bottom],
    ])
    .on('start', brushStart)
    .on('brush', brushed)
    .on('end', brushEnd);

  let svg: SVGElement;
  let selection: Selection<SVGGElement, undefined, SVGElement, undefined>;

  async function setupBrush() {
    // this is needed for when the number of clusters is changed.
    await tick();
    selection = select(svg).selectAll('.brush-group');
    selection.call(brush);
  }

  // TODO: this won't disable brushing after it's enabled
  $: if (svg && pd) {
    setupBrush();
  }

  function adjustClusters(destinationClusterId: number) {
    $cluster_update = {
      feature: copyPd.x_feature,
      prev_num_clusters: copyPd.ice.num_clusters,
      source_cluster_id: sourceClusterId,
      dest_cluster_id: destinationClusterId,
      indices: Array.from(brushedIndices),
    };

    brushedIndices = new Set();
    sourceClusterId = -1;
    selection.call(brush.clear);
  }

  function resetClusters() {
    if (!isAdjusted) {
      return;
    }
    const one_ways = Array.from($one_way_pds);
    delete copyPd.ice.adjusted_clusterings[copyPd.ice.num_clusters];
    one_ways[featureIndex] = copyPd;
    $one_way_pds = one_ways;
  }
</script>

<div class="cluster-lines-container">
  <div class="cluster-lines-header">
    {#if showTitle}
      <div class="cluster-lines-title pdpilot-bold">ICE Clusters</div>
    {/if}
    <div class="cluster-lines-settings">
      {#if brushedIndices.size === 0}
        <div>Number of clusters:</div>
        <div class="num-cluster-change">
          <button
            disabled={copyPd.ice.num_clusters <= 2}
            on:click={() => setNumClusters(copyPd.ice.num_clusters - 1)}
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

          <div class="current-num-clusters">{copyPd.ice.num_clusters}</div>

          <button
            disabled={copyPd.ice.num_clusters === 1 ||
              copyPd.ice.num_clusters >= 5}
            on:click={() => setNumClusters(copyPd.ice.num_clusters + 1)}
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

        {#if isAdjusted}
          <button
            style:margin-left="auto"
            style:margin-right="{margin.right}px"
            on:click={resetClusters}
          >
            Reset Clusters
          </button>
        {/if}
      {:else}
        <div>Move lines to cluster:</div>
        <div class="move-lines">
          <button
            on:click={() => adjustClusters(copyPd.ice.num_clusters)}
            disabled={allLinesInClustedBrushed || copyPd.ice.num_clusters === 5}
          >
            New
          </button>
          {#each clusterIds as clusterId}
            {#if clusterId === sourceClusterId}
              <button class="cluster-number" disabled={true}>
                {clusterId + 1}
              </button>
            {:else}
              <button
                class="cluster-number"
                disabled={copyPd.ice.num_clusters === 2 &&
                  allLinesInClustedBrushed}
                on:click={() => adjustClusters(clusterId)}
                style:--light={light(clusterId)}
                style:--medium={medium(clusterId)}
                style:--dark={dark(clusterId)}
              >
                {clusterId + 1}
              </button>
            {/if}
          {/each}
        </div>
      {/if}
    </div>
  </div>

  {#if showMarginalDistribution}
    <svg {width} height={marginTop}>
      {#if 'bandwidth' in x}
        <MarginalBarChart
          data={feature.distribution}
          {x}
          height={marginalPlotHeight}
          direction="horizontal"
          translate={[0, marginTop - marginalPlotHeight]}
        />
      {:else}
        <MarginalHistogram
          data={feature.distribution}
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
    <svg class="svg-for-clusters" height={chartHeight} {width} bind:this={svg}>
      {#each clusters as cluster}
        <g transform="translate(0,{fy(cluster.id) ?? 0})">
          <YAxis scale={y} x={margin.left} label={'centered prediction'} />
          <XAxis
            scale={x}
            y={facetHeight - margin.bottom}
            showTickLabels={cluster.id === clusterIds[clusterIds.length - 1]}
            showAxisLabel={cluster.id === clusterIds[clusterIds.length - 1]}
            label={copyPd.x_feature}
            integerOnly={feature.subkind === 'discrete'}
            value_map={'value_map' in feature ? feature.value_map : {}}
          />
          <g class="brush-group" id="cluster-{cluster.id}" />
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

  .move-lines {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .cluster-number {
    width: 1.25em;
  }

  .move-lines > .cluster-number:enabled {
    background-color: var(--light);
    border-color: var(--dark);
  }

  .move-lines > .cluster-number:hover:enabled {
    background-color: var(--medium);
  }

  .move-lines > .cluster-number:active:enabled {
    background-color: var(--dark);
  }

  .svg-for-clusters,
  canvas {
    position: absolute;
    top: 0;
    left: 0;
  }
</style>
