<script lang="ts">
	import type { Card, Action } from './interfaces';
	import CardDisplay from './Card.svelte';

	let { cards, action }: { cards?: Array<Card>, action?: Action | undefined } = $props();
</script>

<div class="row">
	{#each cards ?? [] as card, i (i)}
		<CardDisplay {card} {action}  />
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
