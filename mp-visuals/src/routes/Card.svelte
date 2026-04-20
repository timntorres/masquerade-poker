<script lang="ts">
	import type { Card } from './interfaces';
	import { fade, fly } from 'svelte/transition';
	import { SUIT_COLORS, SUIT_SYMBOLS } from './consts';

	let { card }: { card: Card } = $props();

	let rank_ = $derived(card.rank);

	let color = $derived(SUIT_COLORS[card.suit]);
	let symbol = $derived(SUIT_SYMBOLS[card.suit]);
</script>

<div transition:fly={{ y: 10 }} class="card" style="color: {color}">
	<div class="rank">{rank_}</div>
	<div class="suit">{symbol}</div>
</div>

<style>
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
