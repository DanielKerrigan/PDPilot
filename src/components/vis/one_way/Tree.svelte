<script lang="ts">
  import { defaultFormat } from '../../../vis-utils';

  export let node: any;
</script>

{#if node.kind === 'split' && node.children.length > 0}
  <ul
    class="rule-list"
    style:border-left={node.depth === 0 ? 'none' : '1px solid var(--gray-2)'}
  >
    {#each node.children as child}
      <li class="rule-list-item">
        <div>
          <span style:font-weight="bold">{node.depth === 0 ? 'IF' : 'AND'}</span
          >
          {child.feature}
          {#if child.sign === 'gt'}
            >
          {:else if child.sign === 'lte'}
            ≤
          {/if}
          {defaultFormat(child.threshold)}
          {#if child.kind === 'leaf'}
            ({child.num_correct}/{child.num_instances})
          {/if}
        </div>
        <svelte:self node={child} />
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
  }
</style>
