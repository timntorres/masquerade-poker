

<script lang="ts">
  import { SUITS, SUIT_SYMBOLS, SUIT_COLORS } from './suits';

  type Suit = keyof typeof SUITS;

  let { rank, suit }: { rank: string; suit: Suit } = $props();
</script>

<div class="card" style="color: {SUIT_COLORS[suit]}">
  <div class="rank">{rank}</div>
  <div class="suit">{SUIT_SYMBOLS[suit]}</div>
</div>

<style>

    @font-face{
        font-family: 'Klee';
        src: url('KleeOne-Regular.ttf') format(ttf);
        font-display: swap;
    }

    @font-face{
        font-family: 'Apple SD Gothic Neo';
        src: url('AppleSDGothicNeo.ttc') format(ttc);
        font-display: swap;
    }

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
        
        height: 90px;
        aspect-ratio: 64/90;

        border-radius: 11%;
        background-color: #ffffff;

        overflow:hidden;

    }


</style>