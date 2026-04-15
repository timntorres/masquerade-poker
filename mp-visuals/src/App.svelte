<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from './assets/vite.svg'
  import heroImg from './assets/hero.png'
  import Counter from './lib/Counter.svelte'

  import Card from './Card.svelte'

  import { SUITS } from './suits'
  import { readable } from 'svelte/store';

  const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
  const suits = [
    SUITS.HEART,
    SUITS.CLUB,
    SUITS.SPADE,
    SUITS.DIAMOND
  ];

</script>

<div class="container">
  <div class="seat p3">P3</div>
  <div class="seat p4">P4</div>

  <div class="seat p2">P2</div>
  <div class="board">Board</div>
  <div class="seat p5">P5</div>

  <div class="seat p1">P1</div>
  <div class="seat p6">P6</div>

  <div class="dialogue">Dialogue</div>
</div>

<section id="center">


  
  <div class="hero">
    <img src={heroImg} class="base" width="170" height="179" alt="" />
    <img src={svelteLogo} class="framework" alt="Svelte logo" />
    <img src={viteLogo} class="vite" alt="Vite logo" />
  </div>
  <div>
    <h1>Get started</h1>
    <p>Edit <code>src/App.svelte</code> and save to test <code>HMR</code></p>
  </div>
  <Counter />

<div class="grid">
  {#each ranks as rank}
    <div class="row">
      {#each suits as suit}
        <Card {rank} {suit} />
      {/each}
    </div>
  {/each}
</div>

<style>

.container {
  display: grid;
  width: 100%;
  max-width: 1920px;
  height: 1080px;
  margin: 0 auto;

  /* More columns = more control */
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(12, 1fr);

  gap: 8px;
  background: #222;
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
  background: #000;
  border: 2px solid #444;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

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


</section>

<div class="ticks"></div>


<div class="ticks"></div>
<section id="spacer"></section>
