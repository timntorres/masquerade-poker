import datetime
from typing import List, Dict, Set, Optional, ClassVar
from dataclasses import dataclass, field

from constants import Positions as p_
from constants import Actions

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
    amount_in: float = 0

    has_folded: bool = False
    is_all_in: bool = False

    def __repr__(self):
        return self.name

@dataclass(frozen=True)
class Pot:
    player_ids: Set[int]
    amount: float
    parent_pot: Optional['Pot'] = field(default=None)

@dataclass(frozen=True)
class Action:
    phase: str
    subject: str
    subject_id: int
    action: str
    object: str
    time: datetime

    def __str__(self):

        preposition = Actions.PREP_PHRASES[self.action]
        preposition = " " + preposition if preposition != "" else ""
        object =  " " + self.object if self.object != "" else ""

        formatted = f"[{self.time}] {self.subject} {self.action}s{preposition}{object}."

        if(self.action == Actions.IS):
            formatted = f"[{self.time}]{object} – {self.subject}."

        return formatted

    __repr__ = __str__


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
    seats: List[int] = field(default_factory=list)
    btn_index: int = 0

    POSITIONS_PER_PLAYERCOUNT: \
        ClassVar[Dict[int, List[str]]] = {
            2: [p_.BTN, p_.BB],
            3: [p_.BTN, p_.SB, p_.BB],
            4: [p_.BTN, p_.SB, p_.BB, p_.CO],
            5: [p_.BTN, p_.SB, p_.BB, p_.HJ, p_.CO],
            6: [p_.BTN, p_.SB, p_.BB, p_.UTG, p_.HJ, p_.CO]
        }
