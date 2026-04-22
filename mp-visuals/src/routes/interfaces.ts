import { SUITS, RANK_SHORTHAND, POSITIONS, SUBJECTS, ACTIONS, PHASES } from './consts';

export interface Personality {
	id: number;
	name: string;
	traits: string;
	style: string;
	quotes: Array<string>;
}

export interface Player {
	player_id: number;
	name: string;
	position: keyof typeof POSITIONS;
	hole_cards: Card[];
	chips: number;
	personality: Personality;
	amount_in_street: number;
	amount_in_round: number;
	has_folded: boolean;
	is_all_in: boolean;
	prev_id: number;
	next_id: number;
}

export interface Card {
	rank: keyof typeof RANK_SHORTHAND;
	suit: keyof typeof SUITS;
	value: number;
}

export interface Pot {
	ids_involved: Array<number>;
	winning_card_set: Array<Card>;
	amount: number;
}

export interface PotQueue {
	ids_to_bets: Record<number, number>;
	total_amount: number;
	right_pots: Array<Pot>;
}

export interface Snapshot {
	typed_object: string;
	phase: keyof typeof PHASES;
	round_id: number;
	pot_queue: PotQueue;
	community_cards: Card[];
	players: Record<number, Player>;
	seats: number[];
	time: string;
	subject_id: number;
}

export interface Action {
	action_hash: string;
	subject_type: keyof typeof SUBJECTS;
	subject: string;
	action: keyof typeof ACTIONS;
	object: string;
	snapshot: Snapshot;
}
