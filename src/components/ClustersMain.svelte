<script>
  import ClustersGroup from './ClustersGroup.svelte';
  import {
    one_way_quantitative_clusters,
    one_way_categorical_clusters,
    clusteredQuantitativeOneWayPds,
    clusteredCategoricalOneWayPds,
  } from '../stores';
  import { oneWayClustersSortingOptions } from '../sorting';

  $: oneWayClusters = {
    categoricalClusters: $one_way_categorical_clusters,
    quantitativeClusters: $one_way_quantitative_clusters,
    categoricalPds: $clusteredCategoricalOneWayPds,
    quantitativePds: $clusteredQuantitativeOneWayPds,
  };
</script>

<div class="clusters-groups-container">
  <ClustersGroup
    title={'One-way'}
    clusters={oneWayClusters}
    sortingOptions={oneWayClustersSortingOptions}
  />
</div>

<style>
  .clusters-groups-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
</style>
