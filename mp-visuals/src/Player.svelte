<script lang="ts">
    import CardDisplay from './Card.svelte'
  import CardContainer from './CardContainer.svelte';
    import type { Player, Card } from './interfaces';

    let { player }: { player: Player } = $props();
    let chips = $derived(player.chips);
    let name = $derived(player.name);



</script>

<div class="icon"></div>

<CardContainer cards={ player.hole_cards } />

<div class="chipdisplay">
    ${chips.toFixed(2)}
</div>

<div class="overlay">
</div>

<div class="name">
    {name}
</div>


<style>
    .chipdisplay {
        position: absolute;
        font-family: 'Apple SD Gothic Neo';
        font-weight: 100;
        letter-spacing: -.3cqw;

        padding-right: 0.5cqw;

        font-size: 3cqw;
    }

    .icon {
        position: absolute;
        background-color:blue;
        height: 11.5cqw;
        aspect-ratio: 1;
        margin-right: 11cqw;
        border-radius: 50%;
    }

    .overlay {
        position:relative;
        width:100%;
        opacity: .8;
        background-image: linear-gradient(transparent, transparent, transparent, black);
    }

    .name {
        left: 0;
        font-family: 'Apple SD Gothic Neo';
        text-align: left;
        font-size: 2.2cqw;
        font-weight: 300;
        position:absolute;
        margin-left: 1cqw;
        margin-top: 10cqw;
    }

</style>

