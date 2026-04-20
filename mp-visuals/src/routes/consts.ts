export const SUITS = {
	SPADE: 'SPADE',
	HEART: 'HEART',
	DIAMOND: 'DIAMOND',
	CLUB: 'CLUB'
} as const;

export const SUIT_SYMBOLS = {
	SPADE: '♠',
	HEART: '♥',
	DIAMOND: '♦',
	CLUB: '♣'
} as const;

export const SUIT_COLORS = {
	SPADE: '#000000',
	HEART: '#FF0027',
	DIAMOND: '#0027FF',
	CLUB: '#08A000'
} as const;

export const SUIT_SHORTHAND = {
	s: 'SPADE',
	h: 'HEART',
	d: 'DIAMOND',
	c: 'CLUB'
} as const;

export const RANK_SHORTHAND = {
	2: 2,
	3: 3,
	4: 4,
	5: 5,
	6: 6,
	7: 7,
	8: 8,
	9: 9,
	T: 'T',
	J: 'J',
	Q: 'Q',
	K: 'K',
	A: 'A'
} as const;

export const POSITIONS = {
	BTN: 'BTN',
	SB: 'SB',
	BB: 'BB',
	UTG: 'UTG',
	HJ: 'HJ',
	CO: 'CO',
	NONE: ''
};

export const PHASES = {
	GAME_START: 'game start',
	PREFLOP: 'preflop',
	FLOP: 'flop',
	TURN: 'turn',
	RIVER: 'river',
	RESULT: 'result',
	SHOWDOWN: 'showdown',
	GAME_END: 'game end'
};

export const SUBJECTS = {
	DEALER: 'Dealer',
	PLAYER: 'Player'
};

export const PASSIVE_ACTIONS = {
	SHUFFLE: 'shuffle',
	CHECK: 'check',
	CALL: 'call',
	BET: 'bet',
	RAISE: 'raise',
	FOLD: 'fold',
	SAY: 'say',
	THINK: 'think',
	WIN: 'win',
	POST: 'post',
	IS_POSITION: 'is position',
	BUY: 'buy',
	DEALT: 'is dealt',
	COLLECT: 'collect',
	COLLECT_SIDE: 'collect side',
	RETURN: 'return',
	SHOW: 'show',
	FLIP: 'flip',
	EXIT: 'exit'
};

export const ACTIONS = {
	SHUFFLE: 'shuffle',
	CHECK: 'check',
	CALL: 'call',
	BET: 'bet',
	RAISE: 'raise',
	FOLD: 'fold',
	SAY: 'say',
	THINK: 'think',
	WIN: 'win',
	POST: 'post',
	IS_POSITION: 'is position',
	BUY: 'buy',
	DEALT: 'is dealt',
	COLLECT: 'collect',
	COLLECT_SIDE: 'collect side',
	RETURN: 'return',
	SHOW: 'show',
	FLIP: 'flip',
	EXIT: 'exit'
};
