import {
  SUIT_SHORTHAND,
  RANK_SHORTHAND,
  POSITIONS,
  SUBJECTS,
  ACTIONS,
  PHASES,
} from "./consts";

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
  hole_cards: [Card, Card];
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
  suit: keyof typeof SUIT_SHORTHAND;
}

export interface Pot {
  ids_involved: Array<number>;
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
  community_cards: Array<string>;
  players: Record<number, Player>;
  time: string;
  subject_id: number;
}

export interface Action {
  subject_type: keyof typeof SUBJECTS;
  subject: string;
  action: keyof typeof ACTIONS;
  object: string;
  snapshot: Snapshot;
}
