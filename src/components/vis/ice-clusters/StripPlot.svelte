<!--
  Brushing code references
  https://observablehq.com/@d3/brushable-scatterplot-matrix
  https://visualsvelte.com/d3/api/d3-brush
-->
<script lang="ts">
  import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
  import { range } from 'd3-array';
  import { randomInt } from 'd3-random';
  import { brush as d3brush } from 'd3-brush';
  import type { Selection } from 'd3-selection';
  import type { D3BrushEvent } from 'd3-brush';
  import { select } from 'd3-selection';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { FeatureInfo, OneWayPD } from '../../../types';
  import { categoricalColors } from '../../../vis-utils';
  import XAxis from '../axis/XAxis.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let features: string[];

  const margin = {
    top: 10,
    right: 5,
    bottom: 40,
    left: 50,
  };

  const checkBoxHeight = 20;

  const radius = 2;

  $: visHeight = height - checkBoxHeight;

  $: clusterIds = range(pd.ice.clusters.length);

  $: color = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: fy = scaleBand<string>().domain(features).range([0, visHeight]);

  $: y = scaleBand<number>()
    .domain(clusterIds)
    .range([fy.bandwidth() - margin.bottom, margin.top]);

  $: jitterY = randomInt(radius, y.bandwidth() - radius);

  $: I = range($num_instances);

  $: x = Object.fromEntries(
    features.map((f) => {
      const info = $feature_info[f];

      const scale =
        info.kind === 'quantitative'
          ? scaleLinear()
              .domain([info.values[0], info.values[info.values.length - 1]])
              .range([margin.left, width - margin.right])
          : scaleBand<number>()
              .domain(info.values)
              .range([margin.left, width - margin.right])
              .padding(0.1);

      return [f, scale];
    })
  );

  $: data = Object.fromEntries(
    features.map((f) => {
      const info = $feature_info[f];

      let values: number[] = [];

      if (info.subkind === 'one_hot') {
        const cols = info.columns_and_values.map((d) => d[0]);
        values = I.map((i) =>
          cols
            .map((col: string) => $dataset[col][i])
            .findIndex((d: number) => d === 1)
        );
      } else {
        values = $dataset[f];
      }

      const scale = x[f];

      let points: { x: number; y: number; cluster: number }[] = [];

      if ('bandwidth' in scale) {
        const jitterX = randomInt(radius, scale.bandwidth() - radius);

        points = values.map((v, i) => ({
          x: (scale(v) ?? 0) + jitterX(),
          y: (y(pd.ice.cluster_labels[i]) ?? 0) + jitterY(),
          cluster: pd.ice.cluster_labels[i],
        }));
      } else {
        points = values.map((v, i) => ({
          x: scale(v),
          y: (y(pd.ice.cluster_labels[i]) ?? 0) + jitterY(),
          cluster: pd.ice.cluster_labels[i],
        }));
      }

      return [f, points];
    })
  );

  function getValueMap(feature: FeatureInfo) {
    return 'value_map' in feature ? feature.value_map : {};
  }

  // function getX(feature: string, value: number): number {
  //   const scale = x.get(feature);

  //   if (!scale) {
  //     return 0;
  //   }

  //   if ('bandwidth' in scale) {
  //     const jitterX = randomInt(radius, scale.bandwidth() - radius);
  //     return (scale(value) ?? 0) + jitterX();
  //   } else {
  //     return scale(value);
  //   }
  // }

  // brushing
  let defaultColors: boolean[];
  $: defaultColors = new Array($num_instances).fill(true);

  let circleColors: boolean[] = new Array($num_instances).fill(true);

  function brushstarted(this: SVGGElement) {
    brush.move(select(this), null);
  }

  function brushed(this: SVGGElement, { selection }: D3BrushEvent<undefined>) {
    if (selection) {
      const feature = this.id.split('-')[1];
      const [[x0, y0], [x1, y1]] = selection as [
        [number, number],
        [number, number]
      ];

      circleColors = data[feature].map(
        ({ x, y }) => x >= x0 && x <= x1 && y >= y0 && y <= y1
      );
    }
  }

  function brushended({ selection }: D3BrushEvent<undefined>) {
    if (selection) {
      return;
    }

    circleColors = defaultColors;
  }

  $: brush = d3brush<undefined>()
    .extent([
      [margin.left, margin.top],
      [width, fy.bandwidth() - margin.bottom],
    ])
    .on('start', brushstarted)
    .on('brush', brushed)
    .on('end', brushended);

  let group: SVGGElement;
  let selection: Selection<SVGGElement, undefined, SVGElement, undefined>;

  $: if (group) {
    selection = select(group).selectAll('.cell');
    selection.call(brush);
  }
</script>

<div>
  <div style:height="{checkBoxHeight}px" class="controls-container" />
  <svg {width} height={visHeight}>
    <g bind:this={group}>
      {#each Object.entries(data) as [feature, points]}
        <g
          transform="translate(0,{fy(feature)})"
          class="cell"
          id="{jitterY()}-{feature}"
        >
          <g>
            {#each points as { x, y, cluster }, i}
              <circle
                cx={x}
                cy={y}
                r={circleColors[i] ? radius : radius / 2}
                opacity={0.4}
                fill={circleColors[i] ? color(cluster) : 'var(--gray-2)'}
              />
            {/each}
          </g>

          <XAxis
            scale={x[feature]}
            y={fy.bandwidth() - margin.bottom}
            showBaseline={true}
            baselineColor={'var(--gray-6)'}
            tickColor={'var(--gray-6)'}
            integerOnly={$feature_info[feature].subkind === 'discrete'}
            value_map={getValueMap($feature_info[feature])}
            label={feature}
          />
        </g>
      {/each}
    </g>
  </svg>
</div>

<style>
  .label-and-input {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .controls-container {
    display: flex;
    align-items: center;
    gap: 1em;
  }
</style>
