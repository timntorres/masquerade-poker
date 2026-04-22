<script lang="ts">
	import PlayerDisplay from './Player.svelte';
	import Dialogue from './Dialogue.svelte';

	//import { RANK_SHORTHAND, SUIT_SHORTHAND, SUITS } from './consts.ts'

	import Board from './Board.svelte';
	import CardTest from './CardTest.svelte';
	import { players, seats, action, createActionQueue } from './action_queue';
	import { get } from 'svelte/store';

	let props = $props();

	$effect(() => {
		let queue = createActionQueue(props.data?.items, props.data?.audioUrls);
		queue.setInitial(get(queue.actions));
	});
</script>

<div class="container">
	<div class="table"></div>

	{#if $seats[2] != -1 && $players[$seats[2]]}
		<div class="seat p3">
			<PlayerDisplay
				player={$players[$seats[2]]}
				isActive={$players[$seats[2]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		</div>
	{/if}
	<div class="seat p4">
		{#if $seats[3] != -1 && $players[$seats[3]]}
			<PlayerDisplay
				player={$players[$seats[3]]}
				isActive={$players[$seats[3]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		{/if}
	</div>

	<div class="seat p2">
		{#if $seats[1] != -1 && $players[$seats[1]]}
			<PlayerDisplay
				player={$players[$seats[1]]}
				isActive={$players[$seats[1]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		{/if}
	</div>
	<div class="board">
		{#if $action && $seats}
			<Board seats={$seats} action={$action} />
		{/if}
		<!--<CardTest />-->
	</div>
	<div class="seat p5">
		{#if $seats[4] != -1 && $players[$seats[4]]}
			<PlayerDisplay
				player={$players[$seats[4]]}
				isActive={$players[$seats[4]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		{/if}
	</div>

	<div class="seat p1">
		{#if $seats[0] != -1 && $players[$seats[0]]}
			<PlayerDisplay
				player={$players[$seats[0]]}
				isActive={$players[$seats[0]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		{/if}
	</div>
	<div class="seat p6">
		{#if $seats[5] != -1 && $players[$seats[5]]}
			<PlayerDisplay
				player={$players[$seats[5]]}
				isActive={$players[$seats[5]].player_id == $action.snapshot.subject_id}
				action={$action}
			/>
		{/if}
	</div>

	<div class="dialoguebox">
		<Dialogue action={$action} />
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
		position: relative;
		color: white;
		display: flex;
		align-items: top;
		justify-content: right;
	}

	.seat {
		color: white;
		border-radius: 7%;
		overflow: hidden;
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
