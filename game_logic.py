
from game_structs import HoldemRound, Action, Player, Pot
from constants import Phases, Actions, Positions
from deck import Deck
from utils import init_rand, shuffle, get_time, update


import random
import math
import time


def build_log(round: HoldemRound, perspective: Player | None = None) -> str:
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
        
        perspective_exists = perspective is not None
        perspective_differs = perspective_exists and (action.subject_id != perspective.player_id)
        is_dealer = action.subject_id == -1
        must_anonymize = perspective_differs and (not is_dealer)
        if must_anonymize:
            action = Action.anonymize(action)
            
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

    return update(round, actions=action_list)

def init_rand(round, seed=None):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    random.seed(seed)
    round = log_action(round, phase=Phases.GAME_START, subject="Dealer", action=Actions.SHUFFLE, object=f"seed {seed}")
    return round

def shuffle(l):
    random.shuffle(l)
    return l

def refresh_players(round: HoldemRound) -> HoldemRound:
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
    

    return update(round, players=updated_players, seats=updated_seats)
    
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

    return update(round, players=updated_players)

def update_player(round: HoldemRound, player_to_update: Player) -> HoldemRound:

    updated_players = {}
    id_of_updated_player = player_to_update.player_id

    for player in round.players.values():
        id = player.player_id
        if id != id_of_updated_player:
            updated_players[id] = player
            continue
        updated_players[id] = player_to_update

    return update(round, players=updated_players)

def update_pot(round: HoldemRound, updated_amount: float) -> HoldemRound:
    updated_pot = update(round.pot, amount=updated_amount)
    return update(round, pot=updated_pot)

def attempt_bet(round: HoldemRound, player: Player, attempted_amount: int, action: str) -> HoldemRound:
    actual_bet = min(attempted_amount, player.chips)
    updated_chips = player.chips - actual_bet
    updated_amount_in = player.amount_in + actual_bet
    updated_is_all_in = (player.chips == 0)

    new_player = update(player, chips=updated_chips, amount_in=updated_amount_in, is_all_in=updated_is_all_in)

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

        updated_players[current_player.player_id] = update(current_player, hole_cards=hole_cards)

        log_action(round, Phases.GAME_START, current_player.name, Actions.DEALT, str(hole_cards), current_player.player_id)

        ids_seen.add(current_id)
        current_id = current_player.next_id_to_act

    round = update(round, players=updated_players)

    return deck, round

def play_street(round: HoldemRound, phase: str) -> HoldemRound:
    is_preflop = (phase == Phases.PREFLOP)
    bet_occurred = is_preflop
    total_players = round.players.values()

    # Attempt to skip action.

    active_players = []
    for player in total_players:
        if (not player.has_folded) and (not player.is_all_in):
            active_players.append(player)

    action_remains = len(active_players) > 1

    if not action_remains:
        return round

    # Get players by position.

    players_by_position = {}

    for player in total_players:
        players_by_position[player.position] = player
    
    # Big blind ends action preflop.
    last_to_act = players_by_position[Positions.BB]
    
    # Dealer ends action all other streets.
    if phase != Phases.PREFLOP:
        last_to_act = players_by_position[Positions.BTN]
        # If BTN has folded we must find the nearest active player.
        ppp = HoldemRound.POSITIONS_PER_PLAYERCOUNT[total_players]
        ppp_index = ppp.index(Positions.BTN) # Always 0
        while(last_to_act not in active_players):
            ppp_index -= 1
            prev_position = ppp[ppp_index]
            last_to_act = players_by_position[prev_position]

    first_id = last_to_act.next_id_to_act
    current_player = round.players[first_id]

    acted = set() # Flush this each time a player bets.

    #while(current_player not in acted):
    log = build_log(round, current_player)
    print(log)
    
    return round
        # Remember to preserve node relationships upon fold / all-in.


def play_round(round: HoldemRound) -> HoldemRound:
    # Shuffle deck.
    round = init_rand(round)
    button_index = 0
    round = refresh_players(round)
    deck = shuffle(Deck.generate_deck())
    round = set_positions(round)
    round = post_blinds(round)

    deck, round = deal_hole_cards(deck, round)

    # PREFLOP
    
    round = play_street(round, Phases.PREFLOP)

    log_string = build_log(round)
    print(log_string)



