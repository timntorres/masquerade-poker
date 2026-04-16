<script lang="ts">
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from './assets/vite.svg'
  import heroImg from './assets/hero.png'

  import PlayerDisplay from './Player.svelte'

  import type { Player, Card } from './interfaces'
  import { RANK_SHORTHAND, SUIT_SHORTHAND } from './consts'

  import CardTest from './CardTest.svelte'

  import { SUITS } from './consts'
  import { readable } from 'svelte/store';

  let hole_cards: [Card, Card] = [
    {
      rank: 2,
      suit: 'h',
    },
    {
      rank: 2,
      suit: 'c',
    }
  ]

  let player: Player = {
    id: 0,
    name: "Test Name",
    chips: 100,
    position: "HJ",
    hole_cards: hole_cards,
  }

</script>

<div class="container">
  <div class="seat p3">
    <PlayerDisplay {player}/>
  </div>
  <div class="seat p4">
    <PlayerDisplay {player}/>
  </div>

  <div class="seat p2">
    <PlayerDisplay {player}/>
  </div>
  <div class="board">
    <!--<CardTest />-->

  </div>
  <div class="seat p5">
    <PlayerDisplay {player}/>
  </div>

  <div class="seat p1">
    <PlayerDisplay {player}/>
  </div>
  <div class="seat p6">
    <PlayerDisplay {player}/>
  </div>

  <div class="dialogue">Dialogue</div>
</div>




<style>

.container {
  container-type: size;
  display: grid;
  width: 100%;
  max-width: 1920px;
  aspect-ratio: 16/9;
  margin: 0 auto;

  /* More columns = more control */
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(12, 1fr);

  background: #222;
  gap: 2cqw;
}

/* Top players */
.p3 {
  grid-column: 4 / 7;
  grid-row: 1 / 4;
}

.p4 {
  grid-column: 7 / 10;
  grid-row: 1 / 4;
}

/* Left side */
.p2 {
  grid-column: 1 / 4;
  grid-row: 3 / 6;
}

.p1 {
  grid-column: 1 / 4;
  grid-row: 6 / 9;
}

/* Right side */
.p5 {
  grid-column: 10 / 13;
  grid-row: 3 / 6;
}

.p6 {
  grid-column: 10 / 13;
  grid-row: 6 / 9;
}

/* Center board */
.board {

  grid-column: 4 / 10;
  grid-row: 4 / 9;
}

/* Bottom dialogue (offset & centered) */
.dialogue {
  grid-column: 3 / 11;
  grid-row: 9 / -1;
}

.seat, .board, .dialogue {
  overflow: hidden;
  position: relative;
  color: white;
  display: flex;
  align-items: top;
  justify-content: right;
}

.seat {
  border-radius: 10%;
}

.board, .dialogue {
  border: 1px solid #000;
}

</style>


<div class="ticks"></div>


<div class="ticks"></div>
<section id="spacer"></section>
