import { writable, get } from 'svelte/store';
import type { Action, Player, Card, Snapshot, PotQueue, Pot } from './interfaces';
import { ACTIONS } from './consts';
import { SUIT_SHORTHAND } from './consts';

export const players = writable<Record<number, Player>>([]);
export const seats = writable<number[]>([]);
export const action = writable<Action>();
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function runAction(action_: Action) {
	seats.set(action_.snapshot.seats);
	players.set(action_.snapshot.players);
	action.set(action_);

	switch (action_.action) {
		case ACTIONS.SHUFFLE:
			await delay(1000);
			break;
		case ACTIONS.IS_POSITION:
			await delay(125);
			break;
		case ACTIONS.POST:
			await delay(250);
			break;
		case ACTIONS.DEALT:
			await delay(250);
			break;
		case ACTIONS.FLIP:
		case ACTIONS.COLLECT_SIDE:
			await delay(500);
			break;
		default:
			await delay(750);
			break;
	}
}

export function createActionQueue(initial: Action[] = []) {
	const actions = writable<Action[]>(initial);
	const currentAction = writable<Action | null>(null);
	const isProcessing = writable(false);

	function setInitial(actionsList: Action[]) {
		const parsed = actionsList.map((action: Action) => parse_action(action));
		actions.set(parsed);

		processQueue();
	}
	async function processQueue() {
		if (get(isProcessing)) return;
		isProcessing.set(true);

		while (get(actions).length > 0) {
			const queue = get(actions);
			const next = queue[0];

			actions.set(queue.slice(1));
			currentAction.set(next);

			await runAction(next);
			isProcessing.set(false);
		}
		currentAction.set(null);
		isProcessing.set(false);
	}
	return {
		actions,
		currentAction,
		isProcessing,
		setInitial
	};
}

function parse_card(card: Card): Card {
	return {
		...card,
		suit: SUIT_SHORTHAND[card.suit as keyof typeof SUIT_SHORTHAND]
	};
}

function parse_player(player: Player): Player {
	return {
		...player,
		hole_cards: player.hole_cards.map((c: Card) => parse_card(c))
	};
}

function parse_player_record(player_record: Record<number, Player>): Record<number, Player> {
	const players = Object.values(player_record);
	const updated_players = players.map((p: Player) => parse_player(p));
	const updated_record = updated_players.reduce(
		(acc, curr) => {
			acc[curr.player_id] = curr;
			return acc;
		},
		{} as Record<number, Player>
	);
	return updated_record;
}

function parse_right_pot(right_pot: Pot): Pot {
	return {
		...right_pot,
		winning_card_set: right_pot.winning_card_set.map((c: Card) => parse_card(c))
	};
}

function parse_potqueue(potqueue: PotQueue): PotQueue {
	return {
		...potqueue,
		right_pots: potqueue.right_pots.map((r: Pot) => parse_right_pot(r))
	};
}

function parse_snapshot(snapshot: Snapshot): Snapshot {
	return {
		...snapshot,
		community_cards: snapshot.community_cards.map((c: Card) => parse_card(c)),
		players: parse_player_record(snapshot.players),
		pot_queue: parse_potqueue(snapshot.pot_queue)
	};
}

function parse_action(action: Action): Action {
	return {
		...action,
		snapshot: parse_snapshot(action.snapshot)
	};
}
