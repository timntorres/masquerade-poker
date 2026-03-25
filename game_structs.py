import datetime
from typing import List, Dict, ClassVar
from dataclasses import dataclass, field

from constants import Positions as p_

@dataclass(frozen=True)
class Personality:
    id: int
    name: str
    traits: List[str]
    style: str
    quotes: list[str]

@dataclass(frozen=True)
class Player:
    player_id: int
    name: str
    position: str
    personality: Personality

    hole_cards: List[str]
    chips: float
    amount_in: float

    has_folded: bool
    is_all_in: bool

@dataclass(frozen=True)
class Pot:
    players: List[Player]
    amount: float
    parent_pot: 'Pot'

@dataclass(frozen=True)
class Action:
    phase: str
    subject: str
    subject_id: int
    action: str
    object: str
    time: datetime

@dataclass(frozen=True)
class HoldemRound:

    SMALL_BLIND: ClassVar[int] = 1
    BIG_BLIND: ClassVar[int] = 2
    MIN_BUY_IN: ClassVar[int] = 80
    MAX_BUY_IN: ClassVar[int] = 200

    round_id: str
    time: datetime
    pot: Pot
    actions: List[Action]
    
    players: Dict[int, Player] = field(default_factory=dict)

    POSITIONS_PER_PLAYERCOUNT: \
        ClassVar[Dict[int, List[str]]] = {
            2: [p_.BTN, p_.BB],
            3: [p_.BTN, p_.SB, p_.BB],
            4: [p_.BTN, p_.SB, p_.BB, p_.CO],
            5: [p_.BTN, p_.SB, p_.BB, p_.HJ, p_.CO],
            6: [p_.BTN, p_.SB, p_.BB, p_.UTG, p_.HJ, p_.CO]
        }
