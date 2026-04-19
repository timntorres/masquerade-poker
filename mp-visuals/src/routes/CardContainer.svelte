<script lang="ts">
	import type { Card } from './interfaces';
	import CardDisplay from './Card.svelte';

	let { cards }: { cards?: Array<Card> } = $props();
</script>

<div class="row">
	{#each cards ?? [] as card, i (i)}
		<CardDisplay {card} />
	{/each}
</div>

<style>
	.row {
		position: absolute;
		align-items: flex-end;
		height: 13cqw;
		display: flex;

		gap: 0.4cqw;
	}
</style>
