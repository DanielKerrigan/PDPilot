<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';

  export let rules: any;
  export let features: string[];
  export let showFeatureNames: boolean;
</script>

<div class="rule-grid-container" style:--num-columns={features.length}>
  {#if showFeatureNames}
    {#each features as feature}
      <div class="feature-header">{feature}</div>
    {/each}
  {/if}
  {#each rules as rule}
    {#each features as feature}
      <div class="rule-grid-cell">
        {#if feature in rule.conditions}
          <div>
            {#if 'lte' in rule.conditions[feature] && 'gt' in rule.conditions[feature]}
              > {defaultFormat(rule.conditions[feature]['gt'])}, ≤ {defaultFormat(
                rule.conditions[feature]['lte']
              )}
            {:else if 'lte' in rule.conditions[feature]}
              ≤ {defaultFormat(rule.conditions[feature]['lte'])}
            {:else if 'gt' in rule.conditions[feature]}
              > {defaultFormat(rule.conditions[feature]['gt'])}
            {/if}
          </div>
        {/if}
      </div>
    {/each}
  {/each}
</div>

<style>
  .rule-grid-cell {
    border-top: 1px solid var(--gray-1);
  }

  .rule-grid-container {
    display: grid;
    grid-template-columns: repeat(var(--num-columns), 1fr);
    column-gap: 0.25em;
    row-gap: 0.125em;
  }

  .feature-header {
    font-weight: bold;
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
</style>
