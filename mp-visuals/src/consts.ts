export const SUITS = {
  SPADE: "SPADE",
  HEART: "HEART",
  DIAMOND: "DIAMOND",
  CLUB: "CLUB",
} as const;

export const SUIT_SYMBOLS = {
  SPADE: "♠",
  HEART: "♥",
  DIAMOND: "♦",
  CLUB: "♣",
} as const;

export const SUIT_COLORS = {
  SPADE: "#000000",
  HEART: "#FF0027",
  DIAMOND: "#0027FF",
  CLUB: "#08A000",
} as const;

export const SUIT_SHORTHAND = {
  s: "SPADE",
  h: "HEART",
  d: "DIAMOND",
  c: "CLUB",
} as const;

export const RANK_SHORTHAND = {
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  8: "8",
  9: "9",
  t: "10",
  j: "J",
  q: "Q",
  k: "K",
  a: "A",
} as const;
