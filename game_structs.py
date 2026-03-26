import datetime
from typing import List, Dict, Set, Tuple, Optional, ClassVar
from dataclasses import dataclass, field

from constants import Positions as p_
from constants import Actions

from utils import update

@dataclass(frozen=True)
class Personality:
    id: int
    name: str
    traits: str
    style: str
    quotes: Tuple[str]

    def __post_init__(self):
        object.__setattr__(self, "quotes", tuple(self.traits))
        

@dataclass(frozen=True)
class Player:
    player_id: int
    name: str
    position: str
    personality: Personality

    hole_cards: Tuple[str]
    chips: float
    amount_in: float

    has_folded: bool
    is_all_in: bool

    next_id_to_act: int

    def __post_init__(self):
        object.__setattr__(self, "hole_cards", tuple(self.hole_cards))

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

        s = '' if self.action in Actions.DOESNT_ADD_S else 's'

        formatted = f"[{self.time}] {self.subject} {self.action}{s}{preposition}{object}."

        if(self.action == Actions.IS):
            formatted = f"[{self.time}]{object} – {self.subject}."

        return formatted

    @staticmethod
    def anonymize(action):
        anonymized = ""
        if(action.action == Actions.DEALT):
            anonymized = "two cards"
        return update(action, object=anonymized) if anonymized != "" else action


    __repr__ = __str__


@dataclass(frozen=True)
class HoldemRound:

    SMALL_BLIND: ClassVar[int] = 1
    BIG_BLIND: ClassVar[int] = 2
    MIN_BUY_IN: ClassVar[int] = 20
    MAX_BUY_IN: ClassVar[int] = 30

    btn_id: int
    round_id: int
    time: datetime
    pot: Pot
    actions: List[Action]
    
    players: Dict[int, Player]
    seats: List[int]
    community_cards: List[str]

    POSITIONS_PER_PLAYERCOUNT: \
        ClassVar[Dict[int, List[str]]] = {
            2: [p_.BTN, p_.BB],
            3: [p_.BTN, p_.SB, p_.BB],
            4: [p_.BTN, p_.SB, p_.BB, p_.CO],
            5: [p_.BTN, p_.SB, p_.BB, p_.HJ, p_.CO],
            6: [p_.BTN, p_.SB, p_.BB, p_.UTG, p_.HJ, p_.CO]
        }    

