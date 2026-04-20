<script lang="ts">
	import CardContainer from './CardContainer.svelte';
	import type { Player } from './interfaces';
	import { fade } from 'svelte/transition';

	let { player, isActive }: { player: Player; isActive: boolean } = $props();
	let chips = $derived(player.chips);
	let name = $derived(player.name);
</script>

<div transition:fade class={player.is_all_in ? 'container allin' : 'container'}>
	<div class={isActive ? 'icon active' : 'icon'}></div>

	<div class="cardtranslator">
		<CardContainer cards={player.hole_cards} />
	</div>

	<div class="overlay"></div>

	<div class="chipdisplay">
		{#if !player.is_all_in}
			${chips.toFixed(2)}
		{:else}
			ALL-IN
		{/if}
	</div>

	<div class="name">
		{name}
	</div>
</div>

<style>
	.allin {
		color: red;
	}
	.container {
		display: flex;
		position: relative;
		align-items: top;
		justify-content: right;
		width: 100%;
	}

	.chipdisplay {
		position: absolute;
		font-family: 'Apple SD Gothic Neo';
		font-weight: 200;
		letter-spacing: -0.15cqw;

		margin-top: 10.385cqw;

		padding-right: 1cqw;

		font-size: 2cqw;
	}

	.active {
		border: solid;
		border-style: solid;
		color: white;
	}

	.icon {
		box-sizing: border-box;
		border-width: 1px;
		position: absolute;
		background-color: #111;
		height: 11.5cqw;
		aspect-ratio: 1;
		margin-right: 11cqw;
		border-radius: 50%;
	}

	.overlay {
		position: relative;
		width: 100%;
		opacity: 1;
		background-image: linear-gradient(transparent, transparent, transparent, black);
	}

	.name {
		left: 0;
		font-family: 'Apple SD Gothic Neo';
		text-align: left;
		font-size: 1.8cqw;
		font-weight: 700;
		position: absolute;
		margin-left: 1cqw;
		margin-top: 10.5cqw;
	}

	.cardtranslator {
		position: absolute;
		left: 9cqw;
		top: -1.5cqh;
	}
</style>
