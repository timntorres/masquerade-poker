<script lang="ts">
	import { SUIT_SHORTHAND, RANK_SHORTHAND } from './consts';
	import CardDisplay from './Card.svelte';

	const ranks = Object.keys(RANK_SHORTHAND) as Array<keyof typeof RANK_SHORTHAND>;
	const suits = Object.keys(SUIT_SHORTHAND) as Array<keyof typeof SUIT_SHORTHAND>;
</script>

<div class="grid">
	{#each ranks as rank, i (i)}
		<div class="row">
			{#each suits as suit, j (j)}
				<CardDisplay
					card={{
						rank,
						suit: SUIT_SHORTHAND[suit as keyof typeof SUIT_SHORTHAND],
						value: ranks.indexOf(rank) + 2
					}}
				/>
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
