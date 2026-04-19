<script lang="ts">
	import PlayerDisplay from './Player.svelte';
	import Dialogue from './Dialogue.svelte';

	import type { Player, Card } from './interfaces.ts';
	//import { RANK_SHORTHAND, SUIT_SHORTHAND, SUITS } from './consts.ts'

	import Board from './Board.svelte';

	import CardTest from './CardTest.svelte';

	import { players, seats, action, createActionQueue } from './action_queue';

	import { get } from 'svelte/store';

	let props = $props();

	$effect(() => {
		let queue = createActionQueue(props.data?.items);
		queue.setInitial(get(queue.actions));
	});
</script>

<div class="container">
	<div class="table"></div>

	<div class="seat p3">
		{#if $seats[2] && $players[$seats[2]]}
			<PlayerDisplay player={$players[$seats[2]]} />
		{/if}
	</div>
	<div class="seat p4">
		{#if $seats[3] && $players[$seats[3]]}
			<PlayerDisplay player={$players[$seats[3]]} />
		{/if}
	</div>

	<div class="seat p2">
		{#if $seats[1] && $players[$seats[1]]}
			<PlayerDisplay player={$players[$seats[1]]} />
		{/if}
	</div>
	<div class="board">
		{#if $action && $seats}
			<Board seats={$seats} action={$action} />
		{/if}
		<!--<CardTest />-->
	</div>
	<div class="seat p5">
		{#if $seats[4] && $players[$seats[4]]}
			<PlayerDisplay player={$players[$seats[4]]} />
		{/if}
	</div>

	<div class="seat p1">
		{#if $seats[0] && $players[$seats[0]]}
			<PlayerDisplay player={$players[$seats[0]]} />
		{/if}
	</div>
	<div class="seat p6">
		{#if $seats[5] && $players[$seats[5]]}
			<PlayerDisplay player={$players[$seats[5]]} />
		{/if}
	</div>

	<div class="dialoguebox">
		<Dialogue dialogue="This is a dialogue test." />
	</div>
</div>

<CardTest />

<div class="ticks"></div>

<div class="ticks"></div>
<section id="spacer"></section>

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
		opacity: 0.99;
		border-radius: 2cqw 2cqw 0cqw 0cqw;

		grid-column: 3 / 11;
		grid-row: 9 / -1;
	}

	.seat,
	.board {
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
		position: absolute;
		left: 20cqw;
		top: 20cqh;
		width: 60cqw;
		height: 55cqh;
		align-items: center;
		background-color: #411;
		border-radius: 30%;

		box-sizing: border-box;
		border-width: 2cqw;
		border-style: solid;
		border-color: #611;
	}
</style>
