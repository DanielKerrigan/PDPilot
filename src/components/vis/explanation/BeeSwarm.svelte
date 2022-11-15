<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';
  import { double_pdps, globalColorPdpExtent } from '../../../stores';
  import PDP from '../../PDP.svelte';
  import type { DoublePDPData, SinglePDPData } from '../../../types';

  export let node: any;
  export let pd: SinglePDPData;

  let twoWayPdp: DoublePDPData | undefined;
  let showLines: number[] = [];

  function enterFeature(feat: string) {
    twoWayPdp = $double_pdps.find(
      (p) =>
        (p.x_feature === pd.x_feature && p.y_feature === feat) ||
        (p.y_feature === pd.x_feature && p.x_feature === feat)
    );
  }

  function leaveFeature() {
    twoWayPdp = undefined;
  }

  function enterAccuracy(indices: number[]) {
    showLines = indices;
  }

  function leaveAccuracy() {
    showLines = [];
  }
</script>

{#if twoWayPdp !== undefined}
  <div class="pdp-tooltip-container">
    <div class="pdp-tooltip-content">
      <PDP
        pdp={twoWayPdp}
        globalColor={$globalColorPdpExtent}
        width={200}
        height={200}
        scaleLocally={true}
        showTrendLine={false}
        showMarginalDistribution={false}
        showColorLegend={true}
        showInteractions={true}
        clusterDescriptions={'none'}
        iceLevel={'none'}
      />
    </div>
  </div>
{/if}

{#if showLines.length > 0}
  <div class="pdp-tooltip-container">
    <div class="pdp-tooltip-content">
      <PDP
        pdp={pd}
        globalColor={$globalColorPdpExtent}
        width={200}
        height={200}
        scaleLocally={true}
        showTrendLine={false}
        showMarginalDistribution={false}
        showColorLegend={false}
        showInteractions={false}
        clusterDescriptions={'none'}
        iceLevel={'filt'}
        iceLines={showLines}
      />
    </div>
  </div>
{/if}

{#if node.kind === 'split' && node.children.length > 0}
  <ul
    class="rule-list"
    style:border-left={node.depth === 0 ? 'none' : '1px solid var(--gray-2)'}
  >
    {#each node.children as child}
      <li class="rule-list-item">
        <div class="rule-line">
          <div class="rule-part if-and">
            {node.depth === 0 ? 'if' : 'and'}
          </div>
          <div
            class="rule-part feature"
            on:mouseenter={() => enterFeature(child.feature)}
            on:mouseleave={leaveFeature}
          >
            {child.feature}
          </div>
          <div class="rule-part sign">
            {#if child.sign === 'gt'}
              >
            {:else if child.sign === 'lte'}
              ≤
            {/if}
          </div>
          <div class="rule-part threshold">
            {defaultFormat(child.threshold)}
          </div>
          {#if child.kind === 'leaf'}
            <div
              class="accuracy"
              on:mouseenter={() => enterAccuracy(child.indices)}
              on:mouseleave={leaveAccuracy}
            >
              ({child.num_correct}/{child.num_instances})
            </div>
          {/if}
        </div>
        <svelte:self node={child} {pd} />
      </li>
    {/each}
  </ul>
{/if}

<style>
  .rule-list {
    list-style: none;
  }

  .rule-list-item {
    padding-left: 1em;
    margin-top: 0.125em;
  }

  .rule-line {
    display: flex;
    line-height: 1.2;
  }

  .feature {
    background-color: var(--gray-1);
  }

  .accuracy {
    margin-left: auto;
    padding-left: 1em;
  }

  .rule-part + .rule-part {
    margin-left: 0.25em;
  }

  .pdp-tooltip-container {
    position: absolute;
    background-color: white;
    border: 1px solid black;
    pointer-events: none;
    width: 210px;
    height: 210px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pdp-tooltip-content {
    width: 200px;
    height: 200px;
  }
</style>
