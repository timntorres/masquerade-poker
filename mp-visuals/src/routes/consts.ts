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
	WIN: 'win',
	POST: 'post',
	IS_POSITION: 'is position',
	DEALT: 'is dealt',
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

export const IGNORED_ACTIONS = [ACTIONS.IS_POSITION, ACTIONS.DEALT, ACTIONS.FLIP];

export const Grammar = {
	SUBJECT: '%subject%',
	OBJECT: '%object%',
	ALL_IN: '%all_in%',
	STACK: '%stack%'
};

export const PHRASES = {
	SHUFFLE: `${Grammar.SUBJECT} shuffles with seed ${Grammar.OBJECT}.`,
	CHECK: `${Grammar.SUBJECT} checks.`,
	CALL: `${Grammar.SUBJECT} calls${Grammar.ALL_IN}.`,
	BET: `${Grammar.SUBJECT} bets $${Grammar.OBJECT}${Grammar.ALL_IN}.`,
	RAISE: `${Grammar.SUBJECT} raises to $${Grammar.OBJECT}${Grammar.ALL_IN}.`,
	FOLD: `${Grammar.SUBJECT} folds.`,
	SAY: `${Grammar.SUBJECT} says, "${Grammar.OBJECT}"`,
	THINK: `${Grammar.SUBJECT} thinks: *${Grammar.OBJECT}*`,
	WIN: `${Grammar.SUBJECT} wins with $${Grammar.OBJECT} in chips.`,
	POST: `${Grammar.SUBJECT} posts $${Grammar.OBJECT} blind${Grammar.ALL_IN}.`,
	'IS POSITION': `${Grammar.OBJECT} – ${Grammar.SUBJECT} (${Grammar.STACK})`,
	BUY: `${Grammar.SUBJECT} buys in for $${Grammar.OBJECT}.`,
	'IS DEALT': `${Grammar.SUBJECT} is dealt ${Grammar.OBJECT}.`,
	COLLECT: `${Grammar.SUBJECT} collects $${Grammar.OBJECT} from the pot.`,
	'COLLECT SIDE': `${Grammar.SUBJECT} collects $${Grammar.OBJECT} from side pot.`,
	RETURN: `${Grammar.OBJECT}, un-called, returns to ${Grammar.SUBJECT}.`,
	SHOW: `${Grammar.SUBJECT} shows ${Grammar.OBJECT}.`,
	FLIP: `${Grammar.SUBJECT} flips ${Grammar.OBJECT}.`,
	EXIT: `${Grammar.SUBJECT} exits the table.`
};

export const DOLLAR_VALUE_PHRASES = [
	PHRASES.BET,
	PHRASES.RAISE,
	PHRASES.WIN,
	PHRASES.BUY,
	PHRASES.COLLECT,
	PHRASES['COLLECT SIDE']
];
