

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
        font-family: 'Apple SD Gothic Neo';
        font-size: 42px;
        font-weight: 900;
        margin-top: 7px;
        margin-left: 2px;
        margin-bottom:16px;
        letter-spacing: -2px;
    }
    .suit {
        justify-content: left;
        font-size: 70px;
        font-family: 'Klee';
        margin-left: 5px;

    }
    .card {
        width: 64px;
        height: 90px;
        border-radius: 7px;
        background-color: #ffffff;

        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: left;
        overflow:hidden;

    }


</style>