<script lang="ts">
    import CardDisplay from './Card.svelte'
  import CardContainer from './CardContainer.svelte';
    import type { Player, Card } from './interfaces';

    let { player }: { player: Player } = $props();
    let chips = $derived(player.chips);



</script>

    <CardContainer cards={ player.hole_cards } />
<div class="chipdisplay">
    ${chips.toFixed(2)}
</div>


<style>
    .chipdisplay {
        font-family: 'Apple SD Gothic Neo';
        font-weight: 100;
        letter-spacing: -.3cqw;

        padding-right: 0.5cqw;

        font-size: 3.5cqw;
        position: absolute;
    }
</style>

