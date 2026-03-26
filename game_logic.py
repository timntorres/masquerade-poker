
from game_structs import HoldemRound, Action, Player, Pot
from constants import Phases, Actions, Positions
from deck import Deck
from utils import init_rand, shuffle, get_time


import random
import math
import time


def generate_log_string(round: HoldemRound) -> str:
    log_string = ""
    prev_phase = ""
    actions = round.actions

    prev_action_word = ""

    for action in actions:
        # Headers
        if(action.phase != prev_phase):
            log_string += f"\n\n{action.phase.upper()}\n\n"

        # Whitespace between actions of different types.
        if(prev_action_word != "") and (action.action != prev_action_word):
            log_string += "\n"
        prev_action_word = action.action
        
        log_string += f"{action}\n"
        action.action


        prev_phase = action.phase
    return log_string

def log_action(round: HoldemRound, phase: str, subject: str, action: str, object: str, subject_id=-1) -> HoldemRound:
    action_list = round.actions

    money_involved = action == Actions.POST or action == Actions.BET or action == Actions.RAISE or action == Actions.CALL
    if money_involved and round.players[subject_id].is_all_in:
        object += " and is all-in"

    new_action = Action(phase, subject, subject_id, action, object, get_time())
    action_list.append(new_action)

    print(f"ACTION PREVIEW. {new_action}")

    return HoldemRound(
        round.btn_id,
        round.round_id,
        round.time,
        round.pot,
        action_list, #
        round.players,
        round.seats,
    )

def init_rand(round, seed=None):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    random.seed(seed)
    round = log_action(round, phase=Phases.GAME_START, subject="Dealer", action=Actions.SHUFFLE, object=f"seed {seed}")
    return round

def shuffle(l):
    random.shuffle(l)
    return l

def init_players(round: HoldemRound) -> HoldemRound:
    updated_players = {}
    updated_seats = [-1, -1, -1, -1, -1, -1]

    # Reset players' values
    for player in round.players.values():
        updated_player = Player(
            player.player_id, 
            player.name, 
            Positions.NONE, 
            player.personality, 
            [], 
            player.chips, 
            0, 
            False, 
            False,
            player.next_id_to_act
        )
        updated_players[player.player_id] = updated_player
        # Populate updated player in same seat.
        seat_index = round.seats.index(player.player_id)
        updated_seats[seat_index] = updated_player.player_id
    
    return HoldemRound( \
        round.btn_id, round.round_id, round.time, 
        round.pot, round.actions, 
        updated_players, updated_seats
        
    )
    
def set_positions(round: HoldemRound) -> HoldemRound:
    # Set positions.
    position_names = HoldemRound.POSITIONS_PER_PLAYERCOUNT[len(round.players)]

    updated_players = {}

    players_in_seat_order = []

    for player_id in round.seats:
        # Seats can be empty.
        if(player_id == -1):
            continue
        players_in_seat_order.append(round.players[player_id])
    
    btn_index = players_in_seat_order.index(round.players[round.btn_id])

    btn_index_offset = btn_index - len(players_in_seat_order)


    for i in range(btn_index_offset, btn_index_offset + len(players_in_seat_order)):
        player = players_in_seat_order[i]
        new_position = position_names[i]

        updated_players[player.player_id] = Player(
            player.player_id,
            player.name,
            new_position, #
            player.personality,
            player.hole_cards,
            player.chips,
            player.amount_in,
            player.has_folded,
            player.is_all_in,
            players_in_seat_order[(i + 1)%len(players_in_seat_order)].player_id
        )
        round = log_action(
            round, 
            Phases.GAME_START, 
            player.name, 
            Actions.IS, 
            new_position,
            player.player_id
        )

    round = HoldemRound(
        round.btn_id,
        round.round_id,
        get_time(),
        round.pot,
        round.actions,
        updated_players, #
        round.seats
    )

    return round

def update_player(round: HoldemRound, player_to_update: Player) -> HoldemRound:

    updated_players = {}
    id_of_updated_player = player_to_update.player_id

    for player in round.players.values():
        id = player.player_id
        if id != id_of_updated_player:
            updated_players[id] = player
            continue
        updated_players[id] = player_to_update

    return HoldemRound(
        round.btn_id,
        round.round_id,
        round.time,
        round.pot,
        round.actions,
        updated_players, #
        round.seats
    )

def update_pot(round: HoldemRound, updated_amount: float) -> HoldemRound:
    return HoldemRound(
        round.btn_id,
        round.round_id,
        round.time,
        Pot(
            round.pot.player_ids,
            updated_amount, #
            round.pot.parent_pot
        ),
        round.actions,
        round.players,
        round.seats
    )

def attempt_bet(round: HoldemRound, player: Player, attempted_amount: int, action: str) -> HoldemRound:
    actual_bet = min(attempted_amount, player.chips)
    updated_chips = player.chips - actual_bet
    updated_amount_in = player.amount_in + actual_bet
    updated_is_all_in = (player.chips == 0)

    new_player = Player(
        player.player_id,
        player.name,
        player.position,
        player.personality,
        player.hole_cards,
        updated_chips, #
        updated_amount_in, #
        player.has_folded,
        updated_is_all_in,
        player.next_id_to_act
    )

    round = update_player(round, new_player)
    round = update_pot(round, actual_bet)

    object = f"${updated_amount_in}"
    if(action == Actions.POST):
        object += " blind"

    round = log_action(round, Phases.GAME_START, player.name, action, object, player.player_id)

    return round

def post_blinds(round: HoldemRound) -> HoldemRound:


    # Post blinds.
    sb = HoldemRound.SMALL_BLIND
    bb = HoldemRound.BIG_BLIND
    

    sb_id = -1
    bb_id = -1
    for player in round.players.values():
        if (player.position == "SB") or (len(round.players) == 2 and player.position == "BTN"):
            sb_id = player.player_id
        elif (player.position == "BB"):
            bb_id = player.player_id

    round = attempt_bet(round, round.players[sb_id], sb, Actions.POST)
    round = attempt_bet(round, round.players[bb_id], bb, Actions.POST)


    return round

def deal_hole_cards(deck: Deck, round: HoldemRound) -> tuple[Deck, HoldemRound]:
    updated_players = {}

    current_id = round.players[round.btn_id].next_id_to_act

    ids_seen = set()

    while(current_id not in ids_seen):
        current_player = round.players[current_id]
        deck, hole_cards = Deck.pop(deck, 2)

        updated_players[current_player.player_id] = Player(
            current_player.player_id,
            current_player.name,
            current_player.position,
            current_player.personality,
            hole_cards, #
            current_player.chips,
            current_player.amount_in,
            current_player.has_folded,
            current_player.is_all_in,
            current_player.next_id_to_act
        )
        log_action(round, Phases.GAME_START, current_player.name, Actions.DEALT, str(hole_cards), current_player.player_id)

        ids_seen.add(current_id)
        current_id = current_player.next_id_to_act



    for player in round.players.values():

        deck, hole_cards = Deck.pop(deck, 2)
        updated_players[player.player_id] = Player(
            player.player_id,
            player.name,
            player.position,
            player.personality,
            hole_cards,
            player.chips,
            player.amount_in,
            player.has_folded,
            player.is_all_in,
            player.next_id_to_act
        )
    
    round = HoldemRound(
        round.btn_id,
        round.round_id,
        round.time,
        round.pot,
        round.actions,
        updated_players,
        round.seats
    )



    return deck, round

def play_round(round: HoldemRound) -> HoldemRound:
    # Shuffle deck.
    round = init_rand(round)
    button_index = 0
    round = init_players(round)
    deck = shuffle(Deck.generate_deck())
    round = set_positions(round)
    round = post_blinds(round)

    deck, round = deal_hole_cards(deck, round)

    log_string = generate_log_string(round)
    print(log_string)



