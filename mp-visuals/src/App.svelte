<script lang="ts">
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from './assets/vite.svg'
  import heroImg from './assets/hero.png'

  import PlayerDisplay from './Player.svelte'
  import Dialogue from './Dialogue.svelte'

  import type { Player, Card } from './interfaces'
  import { RANK_SHORTHAND, SUIT_SHORTHAND } from './consts'

  import Board from './Board.svelte'

  import { SUITS } from './consts'
  import { readable } from 'svelte/store';

  import CardTest from './CardTest.svelte'

  let hole_cards: [Card, Card] = [
    {
      rank: 2,
      suit: 'd',
    },
    {
      rank: 7,
      suit: 's',
    }
  ]

  let community_cards: [Card, Card, Card, Card, Card] = [
    {
      rank: 't',
      suit: 'h',
    },
    {
      rank: 'j',
      suit: 'h',
    },
    {
      rank: 'k',
      suit: 'h',
    },
    {
      rank: 'q',
      suit: 'h',
    },
    {
      rank: 'a',
      suit: 'h',
    },

  ]

  let player: Player = {
    id: 0,
    name: "TEST NAME",
    chips: 100,
    position: "HJ",
    hole_cards: hole_cards,
  }

</script>

<div class="container">


    <div class="table">
    </div>

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
    <Board {community_cards} pot={569} />
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

  <div class="dialoguebox">
    <Dialogue dialogue={ "This is a dialogue test." }/>
  </div>
</div>


<CardTest />




<style>

.container {
  position: relative;
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
.dialoguebox {

  background-color: rgba(0, 0, 0, 0.7);
  opacity: .99;
  border-radius: 2cqw 2cqw 0cqw 0cqw;

  grid-column: 3 / 11;
  grid-row: 9 / -1;
}



.seat, .board {
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


.table {
  position:absolute;
  left: 20cqw;
  top: 20cqh;
  width:60cqw;
  height:55cqh;
  align-items: center;
  background-color: #411;
  border-radius: 30%;

  box-sizing: border-box;
  border-width: 2cqw;
  border-style: solid;
  border-color: #611;
}

</style>


<div class="ticks"></div>


<div class="ticks"></div>
<section id="spacer"></section>
