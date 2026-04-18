<script lang="ts">
    import type { Card } from './interfaces'
    import CardDisplay from './Card.svelte'

    let { cards }: { cards:Array<Card> } = $props()

    let length = $derived(cards.length)

</script>

<div class="row">
    {#each cards as card}
        <CardDisplay rank={ card.rank } suit={ card.suit } />
    {/each}
</div>

<style>
    .row {        
        position:absolute;
        align-items: flex-end;
        height: 13cqw;
        display: flex;
        
        gap: .4cqw;
    }
</style>