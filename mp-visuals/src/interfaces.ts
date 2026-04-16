import { SUIT_SHORTHAND, RANK_SHORTHAND } from "./consts";

export interface Player {
  id: number;
  name: string;
  position: string;
  hole_cards: [Card, Card];
  chips: number;
}

export interface Card {
  rank: keyof typeof RANK_SHORTHAND;
  suit: keyof typeof SUIT_SHORTHAND;
}
