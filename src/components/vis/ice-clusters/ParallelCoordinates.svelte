<script lang="ts">
  import { scalePoint, scaleLinear, scaleOrdinal } from 'd3-scale';
  import { randomInt } from 'd3-random';
  import { range } from 'd3-array';
  import { line as d3line } from 'd3-shape';
  import { dataset, feature_info, num_instances } from '../../../stores';
  import type { FeatureInfo, OneWayPD } from '../../../types';
  import { categoricalColors } from '../../../vis-utils';
  import YAxis from '../axis/YAxis.svelte';
  import XAxis from '../axis/XAxis.svelte';

  export let pd: OneWayPD;
  export let width: number;
  export let height: number;
  export let features: string[];

  const margin = {
    top: 0,
    right: 20,
    bottom: 0,
    left: 40,
  };

  $: clusterIds = range(pd.ice.clusters.length);

  $: color = scaleOrdinal<number, string>()
    .domain(clusterIds)
    .range(categoricalColors.medium);

  $: y = scalePoint<string>()
    .domain(features)
    .range([margin.top, height - margin.bottom])
    .padding(0.5);

  $: I = range($num_instances);

  $: data = I.map((i) => {
    return features.map((f) => {
      const info = $feature_info[f];
      if (info.subkind !== 'one_hot') {
        return {
          feature: f,
          value: $dataset[f][i],
        };
      } else {
        const cols = info.columns_and_values.map((d: any) => d[0]);

        const val = cols
          .map((col: string) => $dataset[col][i])
          .findIndex((d: number) => d === 1);

        return {
          feature: f,
          value: val,
        };
      }
    });
  });

  $: x = new Map(
    features.map((f) => {
      const info = $feature_info[f];

      const scale =
        info.kind === 'quantitative'
          ? scaleLinear()
              .domain([info.values[0], info.values[info.values.length - 1]])
              .range([margin.left, width - margin.right])
          : scalePoint<number>()
              .domain(info.values)
              .range([margin.left, width - margin.right])
              .padding(0.5);

      return [f, scale];
    })
  );

  type Point = { feature: string; value: number };

  $: lineGenerator = d3line<Point>()
    .x(({ feature, value }) => {
      const scale = x.get(feature);

      if (scale !== undefined) {
        return scale(value) ?? 0;
      } else {
        return 0;
      }
    })
    .y(({ feature }) => y(feature) ?? 0);

  $: tickMarks = (points: Point[]): string => {
    const { feature, value } = points[0];

    const scale = x.get(feature);

    if (scale !== undefined) {
      const xPos = scale(value) ?? 0;
      const yPos = y(feature) ?? 0;

      const yJittered = randomInt(yPos - y.step() / 2, yPos + y.step() / 2)();

      const tickLength = 10;

      return `M ${xPos - tickLength / 2} ${yJittered} h ${tickLength}`;
    } else {
      return '';
    }
  };

  $: line = features.length === 1 ? tickMarks : lineGenerator;

  const getValueMap = (feature: FeatureInfo) =>
    'value_map' in feature ? feature.value_map : {};
</script>

<svg {width} {height}>
  {#each data as d, i}
    <path
      d={line(d)}
      stroke={color(pd.ice.cluster_labels[i])}
      stroke-opacity="0.5"
      fill="none"
    />
  {/each}

  <YAxis
    scale={y}
    x={margin.left}
    showAxisLabel={false}
    tickSize={0}
    gapBetweenTickAndTickLabel={10}
  />

  {#each features as feature}
    <XAxis
      scale={x.get(feature) ?? scaleLinear()}
      y={y(feature)}
      tickLabelOutlineColor="white"
      showBaseline={true}
      baselineColor={'var(--gray-6)'}
      tickColor={'var(--gray-6)'}
      value_map={getValueMap($feature_info[feature])}
    />
  {/each}
</svg>

<style>
</style>
