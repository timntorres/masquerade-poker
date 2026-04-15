<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from './assets/vite.svg'
  import heroImg from './assets/hero.png'
  import Counter from './lib/Counter.svelte'

  import Card from './Card.svelte'

  import { SUITS } from './suits'

  const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
  const suits = [
    SUITS.HEART,
    SUITS.CLUB,
    SUITS.SPADE,
    SUITS.DIAMOND
  ];

</script>

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
