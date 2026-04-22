<script lang="ts">
	import CardContainer from './CardContainer.svelte';
	import { PASSIVE_ACTIONS } from './consts';
	import type { Player, Action } from './interfaces';
	import { fade } from 'svelte/transition';

	let { player, isActive, action }: { player: Player; isActive: boolean; action: Action | undefined } = $props();
	let chips = $derived(player.chips);
	let name = $derived(player.name);
</script>

<div transition:fade class={player.is_all_in ? 'container allin' : 'container'}>
	
	<div class={(isActive && !Object.values(PASSIVE_ACTIONS).includes(action?.action as keyof typeof PASSIVE_ACTIONS)) ? 'icon active' : 'icon'}></div>

	<div class="cardtranslator">
		<CardContainer cards={player.hole_cards} {action} />
	</div>

	<div class="overlay">
		<div class="bottom_row_text">
			<div class="left">
				{#key player.position}
				<div transition:fade class="position">
					{player.position}
				</div>
				{/key}
			</div>

			<div class="name">
				{name}
			</div>

			<div class="chipdisplay right">
				{#if !player.is_all_in}
					${chips.toFixed(2)}
				{:else}
					ALL-IN
				{/if}
			</div>
		</div>
	</div>


</div>

<style>

	.container {
		display: flex;
		position: relative;
		align-items: top;
		justify-content: right;
		width: 100%;
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

		display: flex;
		align-items: flex-end;

		width: 100%;
		opacity: 1;
		background-image: linear-gradient(transparent, transparent, transparent, black);
	}

	.bottom_row_text {
		position: absolute;
		width: 100%;
		display: flex;
		align-items: flex-end;

	}

	.left {
		flex: 0 0 15%;
	}

	.right {
		flex: 0 0 0%;
	}



	.allin {
		color: red;
	}

	.chipdisplay {
		text-align: right;
		white-space: nowrap;
		margin-right: 0.3cqw;
		font-family: 'Apple SD Gothic Neo';
		font-weight: 100;
		letter-spacing: -0.15cqw;

		line-height: 3cqh;


		font-size: 2cqw;
	}

	.name {
		margin-left: 0cqw;
		flex: 1;
		left: 0;
		font-family: 'Apple SD Gothic Neo';
		text-align: left;
		font-size: 1.8cqw;
		line-height: 1.5cqw;
		font-weight: 700;
	}

	.position {
		text-align: center;
		line-height: 2.3cqh;
		font-family: 'Apple SD Gothic Neo';
		font-weight: 100;
		font-size: 1.5cqw;
	}



	.cardtranslator {
		position: absolute;
		left: 9cqw;
		top: -1.5cqh;
	}
</style>
