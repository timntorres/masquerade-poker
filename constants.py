from dataclasses import dataclass, field
from typing import Dict, ClassVar

from enum import Enum

class Positions (str, Enum):
    BTN = "BTN"
    SB = "SB"
    BB = "BB"
    UTG = "UTG"
    HJ = "HJ"
    CO = "CO"

    NONE = ""

@dataclass(frozen=True)
class Phases:
    GAME_START: ClassVar[str] = "game start"
    PREFLOP: ClassVar[str] = "preflop"
    FLOP: ClassVar[str] = "flop"
    TURN: ClassVar[str] = "turn"
    RIVER: ClassVar[str] = "river"
    GAME_END: ClassVar[str] = "game end"

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
    IS: ClassVar[str] = 'is'
    BUY: ClassVar[str] = 'buy'
    DEALT: ClassVar[str] = 'is dealt'

    DOESNT_ADD_S: ClassVar[set] = set([DEALT])

    PREP_PHRASES: ClassVar[Dict[str, str]] = {
        SHUFFLE: 'with',
        CHECK: '',
        CALL: '',
        BET: '',
        RAISE: 'to',
        FOLD: '',
        SAY: '',
        THINK: '',
        WIN: '',
        POST: '',
        IS: '',
        BUY: 'in for',
        DEALT: ''
    }
