<script lang="ts">
	import { fly } from 'svelte/transition';
	import CardContainer from './CardContainer.svelte';
	import type { Action } from './interfaces';
	import { POSITIONS } from './consts';

	let { seats, action }: { seats: number[]; action: Action } = $props();
</script>

<div class="container">
	<!-- Seat 1 -->
	{#if seats[0] != -1}
		{#if action.snapshot.players[seats[0]].amount_in_street > 0}
			<div class="betlocation a">
				<div class="bet">${action.snapshot.players[seats[0]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
		{#if action.snapshot.players[seats[0]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation b">B</div>
		{/if}
	{/if}

	<!-- Seat 2 -->
	{#if seats[1] != -1}
		{#if action.snapshot.players[seats[1]].amount_in_street > 0}
			<div class="betlocation d">
				<div class="bet">${action.snapshot.players[seats[1]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
		{#if action.snapshot.players[seats[1]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation c">B</div>
		{/if}
	{/if}

	<!-- Seat 3 -->
	{#if seats[2] != -1}
		{#if action.snapshot.players[seats[2]].amount_in_street > 0}
			<div class="betlocation f">
				<div class="bet">${action.snapshot.players[seats[2]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
		{#if action.snapshot.players[seats[2]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation e">B</div>
		{/if}
	{/if}

	<!-- Seat 4 -->
	{#if seats[3] != -1}
		{#if action.snapshot.players[seats[3]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation g">B</div>
		{/if}
		{#if action.snapshot.players[seats[3]].amount_in_street > 0}
			<div class="betlocation h">
				<div class="bet">${action.snapshot.players[seats[3]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
	{/if}

	<!-- Seat 5 -->
	{#if seats[4] != -1}
		{#if action.snapshot.players[seats[4]].amount_in_street > 0}
			<div class="betlocation rightalign i">
				<div class="bet">${action.snapshot.players[seats[4]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
		{#if action.snapshot.players[seats[4]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation j">B</div>
		{/if}
	{/if}

	<!-- Seat 6 -->
	{#if seats[5] != -1}
		{#if action.snapshot.players[seats[5]].amount_in_street > 0}
			<div class="betlocation rightalign l">
				<div class="bet">${action.snapshot.players[seats[5]].amount_in_street.toFixed(2)}</div>
			</div>
		{/if}
		{#if action.snapshot.players[seats[5]].position == POSITIONS.BTN}
			<div transition:fly={{ y: 5 }} class="btnlocation k">B</div>
		{/if}
	{/if}

	<div class="board center">
		<CardContainer cards={action.snapshot.community_cards} {action} />
		<div class="pot center">
			${action.snapshot.pot_queue.total_amount.toFixed(2)}
		</div>
	</div>
</div>

<style>
	.center {
		grid-area: 2 / 2 / 11 / 12;
	}

	.l {
		grid-area: 6 / 12 / 7 / 13;
	}

	.k {
		grid-area: 5 / 12 / 6 / 13;
	}

	.j {
		grid-area: 3 / 12 / 4 / 13;
	}

	.i {
		grid-area: 2 / 12 / 3 / 13;
	}

	.h {
		grid-area: 1 / 10 / 2 / 11;
	}

	.g {
		grid-area: 1 / 9 / 2 / 10;
	}

	.f {
		grid-area: 1 / 4 / 2 / 5;
	}

	.e {
		grid-area: 1 / 3 / 2 / 4;
	}

	.d {
		grid-area: 2 / 1 / 3 / 2;
	}

	.c {
		grid-area: 3 / 1 / 4 / 2;
	}

	.b {
		grid-area: 5 / 1 / 6 / 2;
	}

	.a {
		grid-area: 6 / 1 / 7 / 2;
	}

	.bet {
		position: absolute;
		font-family: 'Apple SD Gothic Neo';
		font-size: 3cqw;
		font-weight: 300;
		letter-spacing: -0.15cqw;
	}

	.betlocation {
		position: relative;
	}

	.btnlocation {
		background-image: linear-gradient(white, lightgray);
		border-style: solid;
		border-width: 0.5cqw;
		justify-content: center;
		text-align: center;

		box-sizing: border-box;
		width: 3cqw;
		height: 3cqw;
		border-radius: 50%;
		border-color: white;
		color: darkslategray;
		font-family: 'Apple SD Gothic Neo';
		font-size: 2cqw;
		font-weight: 900;
	}

	.container {
		display: grid;
		width: 100%;
		grid-template-columns: repeat(12, 1fr);
		grid-template-rows: repeat(6, 1fr);
	}

	.board {
		margin-left: 2.5cqw;
	}

	.pot {
		position: absolute;
		margin-top: 28cqh;
		margin-left: 12cqw;

		font-size: 3.5cqw;
		font-family: 'Apple SD Gothic Neo';
		font-weight: 800;
	}

	.rightalign {
		display: flex;
		justify-content: flex-end;
		align-items: center;
	}
</style>
