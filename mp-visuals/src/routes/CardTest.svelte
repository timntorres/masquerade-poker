
<script lang="ts">

  import { SUIT_SHORTHAND, RANK_SHORTHAND } from "./consts";
  import CardDisplay from "./Card.svelte";

  const ranks = Object.keys(RANK_SHORTHAND) as Array<keyof typeof RANK_SHORTHAND>;
  const suits = Object.keys(SUIT_SHORTHAND) as Array<keyof typeof SUIT_SHORTHAND>;

</script>

<div class="grid">
  {#each ranks as rank}
    <div class="row">
      {#each suits as suit}
        <CardDisplay {rank} {suit} />
      {/each}
    </div>
  {/each}
</div>

<style>
  .grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .row {
    display: flex;
    gap: 8px;
  }
</style>