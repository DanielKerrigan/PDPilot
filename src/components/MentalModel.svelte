<script lang="ts">
  import { feature_names, one_way_pds, two_way_pds } from '../stores';
  import { scaleLinear, scaleQuantize } from 'd3-scale';

  let mode: 'edit' | 'view' = 'edit';

  let importantFeatures: string[] = [];
  let importantFeature: string = '';

  function addFeature() {
    if (
      importantFeature !== '' &&
      !importantFeatures.includes(importantFeature)
    ) {
      importantFeatures = [...importantFeatures, importantFeature];
    }
  }

  function removeFeature(feature: string) {
    importantFeatures = importantFeatures.filter((f) => f !== feature);
  }

  $: feature_to_rank = Object.fromEntries(
    $one_way_pds.map((d, i) => [
      d.x_feature,
      { rank: i + 1, deviation: d.deviation },
    ])
  );

  $: maxDeviation = Math.max(
    ...Object.values(feature_to_rank).map((d) => d.deviation)
  );

  $: deviationScale = scaleLinear().domain([0, maxDeviation]).range([0, 100]);
  $: featureRankScale = scaleQuantize<string>()
    .domain([1, $feature_names.length])
    .range([
      'rgba(89, 161, 79, 0.5)',
      'rgba(237, 201, 73, 0.5)',
      'rgba(225, 87, 89, 0.5)',
    ]);

  function pairToString(a: string, b: string) {
    return a + ' - ' + b;
  }

  let interactingFeaturePairs: string[] = [];
  let interactingFeature1: string = '';
  let interactingFeature2: string = '';

  $: pair_to_rank = Object.fromEntries(
    $two_way_pds.map((d, i) => [
      pairToString(d.x_feature, d.y_feature),
      { rank: i + 1, H: d.H },
    ])
  );

  $: hValues = Object.values(pair_to_rank).map((d) => d.H);

  $: maxH = Math.max(...hValues);
  $: minH = Math.min(...hValues);

  $: hScale = scaleLinear().domain([minH, maxH]).range([0, 100]);
  $: pairRankScale = scaleQuantize<string>()
    .domain([1, $two_way_pds.length])
    .range([
      'rgba(89, 161, 79, 0.5)',
      'rgba(237, 201, 73, 0.5)',
      'rgba(225, 87, 89, 0.5)',
    ])
    .unknown('rgba(225, 87, 89, 0.5)');

  function addFeaturePair() {
    let [a, b] = [interactingFeature1, interactingFeature2].sort();
    let pair = pairToString(a, b);

    if (pair.length >= 3 && !interactingFeaturePairs.includes(pair)) {
      interactingFeaturePairs = [...interactingFeaturePairs, pair];
    }
  }

  function removeFeaturePair(pair: string) {
    interactingFeaturePairs = interactingFeaturePairs.filter((p) => p !== pair);
  }
</script>

<div class="mental-model-container">
  <div class="mental-model-header">
    <h1>Mental Model</h1>
    <div class="view-or-edit">
      <label><input type="radio" bind:group={mode} value="edit" /> Edit</label>
      <label><input type="radio" bind:group={mode} value="view" /> View</label>
    </div>
  </div>
  <div class="mental-model-content">
    {#if mode === 'edit'}
      <div class="mental-model-section">
        <h2>Feature Importance</h2>
        <p>What features do you expect to be most important?</p>

        <div>
          <input list="features-datalist" bind:value={importantFeature} />
          <datalist id="features-datalist">
            {#each $feature_names as feature_name}
              <option value={feature_name} />
            {/each}
          </datalist>
          <button on:click={addFeature}>Add</button>
        </div>

        <div>
          {#each importantFeatures as feature}
            <div class="feature-row">
              <button on:click={() => removeFeature(feature)}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="icon icon-tabler icon-tabler-x"
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
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
              <div>{feature}</div>
            </div>
          {/each}
        </div>
      </div>
      <div class="mental-model-section">
        <h2>Feature Interaction</h2>
        <p>
          What pairs of features do you expect to have the most interaction?
        </p>

        <div>
          <input list="features-datalist" bind:value={interactingFeature1} />
          <input list="features-datalist" bind:value={interactingFeature2} />
          <datalist id="features-datalist">
            {#each $feature_names as feature_name}
              <option value={feature_name} />
            {/each}
          </datalist>
          <button on:click={addFeaturePair}>Add</button>
        </div>

        <div>
          {#each interactingFeaturePairs as pair}
            <div class="feature-row">
              <button on:click={() => removeFeaturePair(pair)}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="icon icon-tabler icon-tabler-x"
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
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
              <div>{pair}</div>
            </div>
          {/each}
        </div>
      </div>
      <div class="mental-model-section">
        <h2>Constraints</h2>
      </div>
    {:else}
      <div class="mental-model-section">
        <h2>Feature Importance</h2>
        <table>
          <thead>
            <tr>
              <th scope="col">Feature</th>
              <th scope="col" class="number-col">Rank</th>
              <th scope="col">Deviation</th>
            </tr>
          </thead>
          <tbody>
            {#each importantFeatures as f}
              <tr>
                <td>{f}</td>
                <td class="number-col">
                  <div
                    style:background={featureRankScale(feature_to_rank[f].rank)}
                  >
                    {feature_to_rank[f].rank}
                  </div>
                </td>
                <td>
                  <div
                    style:width="{deviationScale(
                      feature_to_rank[f].deviation
                    )}%"
                    style:height="1em"
                    style:background="var(--gray-4)"
                  />
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <div class="mental-model-section">
        <h2>Feature Interaction</h2>
        <table>
          <thead>
            <tr>
              <th scope="col">Pair</th>
              <th scope="col" class="number-col">Rank</th>
              <th scope="col">H-statistic</th>
            </tr>
          </thead>
          <tbody>
            {#each interactingFeaturePairs as pair}
              <tr>
                <td>{pair}</td>
                <td class="number-col">
                  <div
                    style:background={pairRankScale(pair_to_rank[pair]?.rank)}
                  >
                    {pair_to_rank[pair]?.rank ?? 'N/A'}
                  </div>
                </td>
                <td>
                  <div
                    style:width="{hScale(pair_to_rank[pair]?.H ?? minH)}%"
                    style:height="1em"
                    style:background="var(--gray-4)"
                  >
                    {#if !pair_to_rank.hasOwnProperty(pair)}
                      N/A
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <div class="mental-model-section">
        <h2>Constraints</h2>
      </div>
    {/if}
  </div>
</div>

<style>
  /* https://stackoverflow.com/a/69029387/5016634 */
  .icon-tabler-x {
    -webkit-transform: translate(0px, 0px);
    transform: translate(0px, 0px);
  }

  .feature-row {
    display: flex;
    align-items: center;
    gap: 0.25em;
  }

  .mental-model-container {
    width: 100%;
    height: 100%;

    display: flex;
    flex-direction: column;

    padding: 1em;
  }

  .mental-model-section {
    margin-top: 1em;
  }

  .mental-model-section > * + * {
    margin-top: 0.5em;
  }

  /* .mental-model-section > h2 {
    margin-bottom: 0.5em;
  } */

  .mental-model-header {
    display: flex;
    align-items: center;
    gap: 2em;
  }

  .view-or-edit {
    display: flex;
    gap: 1em;
  }

  table {
    border-collapse: collapse;
    table-layout: fixed;
  }

  th {
    text-transform: uppercase;
    font-weight: normal;
  }

  .number-col {
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  /* add padding between columns, but not on outside of table.
   From https://observablehq.com/@tmcw/fancy-tables
  */
  th:not(:first-child):not(:last-child),
  td:not(:first-child):not(:last-child) {
    padding: 0 0.5em;
  }

  tr:not(:last-child) {
    border-bottom: 1px solid var(--gray-3);
  }
</style>
