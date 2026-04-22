<script lang="ts">
	import { writable, get } from 'svelte/store'
	import type { Card, Action } from './interfaces';
	import { fade, fly } from 'svelte/transition';
	import { PHASES, SUIT_COLORS, SUIT_SYMBOLS } from './consts';

	let { card, action }: { card: Card, action: Action | undefined } = $props();

	let rank_ = $derived(card.rank);

	let color = $derived(SUIT_COLORS[card.suit]);
	let symbol = $derived(SUIT_SYMBOLS[card.suit]);

	const is_included = writable<boolean>(true);

	$effect(() => {
		let is_showdown = action?.snapshot.phase == PHASES.SHOWDOWN;
		let pot = action?.snapshot.pot_queue.right_pots.at(-1);
		let winning_cards = pot?.winning_card_set;
		let is_uncalled_surplus = pot?.ids_involved.length != undefined && pot?.ids_involved.length == 1;
		let empty = (winning_cards != undefined) && winning_cards.length === 0;

		if(winning_cards === undefined || empty || !is_showdown || is_uncalled_surplus) {
			is_included.set(true);
			return;
		}

		let included = winning_cards.some(c => card.rank === c.rank && card.suit === c.suit );
		is_included.set(included);
	});


</script>

<div transition:fly={{ y: 10 }} class={$is_included ? "card" : "card exclusion"} style="color: {color}">
	<div class="rank">{rank_}</div>
	<div class="suit">{symbol}</div>
</div>

<style>

	.exclusion {
		opacity: 0.35;
		transform: translate(0, 1cqw);

	}

	.rank {
		position: absolute;
		opacity: 0.9;
		top: -2cqw;
		left: 7cqw;
		font-size: 60cqw;
		font-family: 'Apple SD Gothic Neo';
		font-weight: 900;
		letter-spacing: -5cqw;
	}
	.suit {
		opacity: 0.7;
		position: absolute;
		bottom: -25cqw;
		right: -15cqw;
		font-size: 100cqw;
		font-family: 'Klee';
	}
	.card {
		position: relative;
		container-type: size;

		height: 9.5cqw;
		aspect-ratio: 64/90;

		border-radius: 11%;
		background-color: #ffffff;

		overflow: hidden;
	}
</style>
