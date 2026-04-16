

<script lang="ts">
  import { SUIT_SHORTHAND, RANK_SHORTHAND, SUIT_SYMBOLS, SUIT_COLORS } from './consts';

  let { rank, suit }: { rank: keyof typeof RANK_SHORTHAND; suit: keyof typeof SUIT_SHORTHAND } = $props();
  
  let suit_ = $derived(SUIT_SHORTHAND[suit]);
  let rank_ = $derived(RANK_SHORTHAND[rank]);

  let color = $derived(SUIT_COLORS[suit_]);
  let symbol = $derived(SUIT_SYMBOLS[suit_]);

</script>

<div class="card" style="color: { color }">
  <div class="rank">{ rank_ }</div>
  <div class="suit">{ symbol }</div>
</div>

<style>

    .rank {
        position: absolute;
        opacity: .9;
        top: -2cqw;
        left: 7cqw;
        font-size: 80cqw;
        font-family: 'Apple SD Gothic Neo';
        font-weight: 900;
        letter-spacing: -5cqw;
    }
    .suit {
        opacity: .45;
        position: absolute;
        bottom: -50cqw;
        right: -50cqw;
        font-size: 120cqw;
        font-family: 'Klee';

    }
    .card {
        position: relative;
        container-type: size;
        
        height: 9.5cqw;
        aspect-ratio: 64/90;

        border-radius: 11%;
        background-color: #ffffff;

        overflow:hidden;

    }


</style>