from dataclasses import dataclass, field
from typing import Dict, ClassVar

from enum import Enum

@dataclass (frozen = True)
class Positions:
    BTN: str = "BTN"
    SB: str = "SB"
    BB: str = "BB"
    UTG: str = "UTG"
    HJ: str = "HJ"
    CO: str = "CO"

    NONE = ""

class Phases (str, Enum):
    GAME_START = "game start"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    RESULT = "result"
    SHOWDOWN = "showdown"
    GAME_END = "game end"

@dataclass (frozen=True)
class Grammar:
    SUBJECT: str = "%subject%"
    OBJECT: str = "%object%"
    ALL_IN: str = "%all_in%"
    STACK: str = "%stack%"

@dataclass (frozen=True)
class Subjects:
    DEALER: str = "Dealer"
    PLAYER: str = "Player"
    DEALER_ID: int = -1

@dataclass(frozen=True)
class Actions:

    SHUFFLE: ClassVar[str] = 'shuffle'
    CHECK: ClassVar[str] = 'check'
    CALL: ClassVar[str] = 'call'
    BET: ClassVar[str] = 'bet'
    RAISE: ClassVar[str] = 'raise'
    FOLD: ClassVar[str] = 'fold'
    SAY: ClassVar[str] = 'say'
    THINK: ClassVar[str] = 'think'
    WIN: ClassVar[str] = 'win'
    POST: ClassVar[str] = 'post'
    IS_POSITION: ClassVar[str] = 'is position'
    BUY: ClassVar[str] = 'buy'
    DEALT: ClassVar[str] = 'is dealt'
    COLLECT: ClassVar[str] = 'collect'
    COLLECT_SIDE: ClassVar[str] = 'collect side'
    RETURN: ClassVar[str] = 'return'
    SHOW: ClassVar[str] = 'show'
    FLIP: ClassVar[str] = 'flip'

    DOESNT_ADD_S: ClassVar[set] = set([DEALT])
    MONEY_INVOLVED: ClassVar[set] = set([POST, BET, RAISE, CALL])

    PHRASES: ClassVar[Dict[str, str]] = {
        SHUFFLE: f'{Grammar.SUBJECT} shuffles with seed {Grammar.OBJECT}.',
        CHECK: f'{Grammar.SUBJECT} checks.',
        CALL: f'{Grammar.SUBJECT} calls{Grammar.ALL_IN}.',
        BET: f'{Grammar.SUBJECT} bets ${Grammar.OBJECT}{Grammar.ALL_IN}.',
        RAISE: f'{Grammar.SUBJECT} raises to ${Grammar.OBJECT}{Grammar.ALL_IN}.',
        FOLD: f'{Grammar.SUBJECT} folds.',
        SAY: f'{Grammar.SUBJECT} says, "{Grammar.OBJECT}"',
        THINK: f'{Grammar.SUBJECT} thinks: *{Grammar.OBJECT}*',
        WIN: f'{Grammar.SUBJECT} wins with ${Grammar.OBJECT} in chips.',
        POST: f'{Grammar.SUBJECT} posts ${Grammar.OBJECT} blind{Grammar.ALL_IN}.',
        IS_POSITION: f'{Grammar.OBJECT} – {Grammar.SUBJECT} ({Grammar.STACK})',
        BUY: f'{Grammar.SUBJECT} buys in for ${Grammar.OBJECT}.',
        DEALT: f'{Grammar.SUBJECT} is dealt {Grammar.OBJECT}.',
        COLLECT: f'{Grammar.SUBJECT} collects ${Grammar.OBJECT} from the pot.',
        COLLECT_SIDE: f'{Grammar.SUBJECT} collects ${Grammar.OBJECT} from side pot.',
        RETURN: f'${Grammar.OBJECT}, un-called, returns to {Grammar.SUBJECT}.',
        SHOW: f'{Grammar.SUBJECT} shows {Grammar.OBJECT}.',
        FLIP: f'{Grammar.SUBJECT} flips {Grammar.OBJECT}.'
    }
