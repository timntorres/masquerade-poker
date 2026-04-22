import datetime
from typing import List, Dict, Set, Tuple, Optional, ClassVar, TypeVar, Generic
from dataclasses import dataclass, field

from constants import Positions as p_
from constants import Actions, Subjects, Grammar

from utils import update

@dataclass(frozen=True)
class Personality:
    id: int
    name: str
    traits: str
    style: str
    quotes: Tuple[str]

    def __post_init__(self):
        object.__setattr__(self, "quotes", tuple(self.quotes))
        

@dataclass(frozen=True)
class Player:
    player_id: int
    name: str
    position: str
    personality: Personality

    hole_cards: Tuple[str]
    chips: float
    # For calculating bet sizes
    amount_in_street: float
    # For calculating all-in stack size
    amount_in_round: float

    has_folded: bool
    is_all_in: bool

    prev_id: int
    next_id: int

    def __post_init__(self):
        object.__setattr__(self, "hole_cards", tuple(self.hole_cards))

    def __repr__(self):
        return self.name

@dataclass(frozen=True)
class Pot: 
    ids_involved: List[int]
    winning_card_set: List[str]
    amount: float

@dataclass(frozen=True)
class PotQueue:
    # A key insight is that side pots only ever matter when a non stack-leader is all-in.
    # Once that player is all-in, the amount that player can win is now capped.
    # This means side pots only ever matter when the short-stacked, all-in player wins the hand.
    # Another core principle is to model the behavior and timing after what actual human Dealers do.

    ids_to_bets: Dict[int, float]
    total_amount: float
    right_pots: List[Pot]

T = TypeVar("T")

@dataclass(frozen=True)
class Snapshot(Generic[T]):
    typed_object: T
    phase: str
    round_id: int
    pot_queue: PotQueue
    community_cards: Tuple[str]
    players: Dict[int, Player]
    seats: List[int]
    time: datetime
    subject_id: int = -1

    def __post_init__(self):
        object.__setattr__(self, "community_cards", tuple(self.community_cards))


@dataclass(frozen=True)
class Action():
    action_hash: str
    subject_type: str
    subject: str
    action: str
    object: str
    snapshot: Snapshot

    def __str__(self):
        phrase = Actions.PHRASES[self.action]

        subject = self.subject

        if (Grammar.STACK in phrase) and (self.subject_type != Subjects.DEALER):
            players = self.snapshot.players
            id = self.snapshot.subject_id
            phrase = phrase.replace(Grammar.STACK, f"${players[id].chips}")

        phrase = phrase.replace(Grammar.SUBJECT, subject)
        phrase = phrase.replace(Grammar.OBJECT, self.object)
        all_in = False

        if (self.subject_type == Subjects.PLAYER):
            id = self.snapshot.subject_id
            player = self.snapshot.players[id]
            all_in = player.is_all_in
    
        all_in_phrase = " and is all-in" if all_in else ""        
        phrase = phrase.replace(Grammar.ALL_IN, all_in_phrase)
        return phrase

    @staticmethod
    def anonymize(action):
        anonymized = ""
        if(action.action == Actions.DEALT):
            anonymized = "[??, ??]"
        return update(action, object=anonymized) if anonymized != "" else action


    __repr__ = __str__


@dataclass(frozen=True)
class HoldemRound:

    SMALL_BLIND: ClassVar[int] = 1
    BIG_BLIND: ClassVar[int] = 2
    MIN_BUY_IN: ClassVar[int] = 20
    MAX_BUY_IN: ClassVar[int] = 30

    phase: str
    round_id: int
    date: datetime
    time: datetime
    pot_queue: PotQueue
    actions: List[Action]
    
    players: Dict[int, Player]
    seats: List[int]
    community_cards: List[str]

    seat_index_of_btn: int = -1

    POSITIONS_PER_PLAYERCOUNT: \
        ClassVar[Dict[int, List[str]]] = {
            2: [p_.BTN, p_.BB],
            3: [p_.BTN, p_.SB, p_.BB],
            4: [p_.BTN, p_.SB, p_.BB, p_.CO],
            5: [p_.BTN, p_.SB, p_.BB, p_.HJ, p_.CO],
            6: [p_.BTN, p_.SB, p_.BB, p_.UTG, p_.HJ, p_.CO]
        }    

