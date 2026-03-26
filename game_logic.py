
from game_structs import HoldemRound, Action, Player, Pot
from constants import Phases, Actions, Positions
from deck import Deck
from utils import init_rand, shuffle, get_time, update

import anthropic

import random
import math
import time

def build_prompt(round: HoldemRound, player: Player, bet_occurred: bool, highest_bet: float, min_raise: float) -> str:
        """
        CASES
        1. bet, check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind?
                Yes
        2. bet (all in), check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind?
                No
            
        3. call (all in), fold
            Has anyone else bet this street?
                Yes
            Does the previous bettor have me covered?
                Yes

        4. raise (all in), call, fold
            Has anyone else bet this street?
                Yes
            Does the previous bettor have me covered?
                No
            Can I min raise with chips to spare?
                No

        5. raise, call, fold
            Has anyone else bet this street? 
                Yes
            Does the previous bettor have me covered?
                No
            Can I min raise with chips to spare?
                Yes
        """

        prev_highest_bet = highest_bet
        amount_to_call = prev_highest_bet - player.amount_in
        """Betting / Checking logic"""
        # Has anyone else bet this street?
        prev_bet_exists = bet_occurred
        # Can I afford to bet more than the minimum bet?
        can_afford_min_bet = player.chips > min_raise
        """Raising / Calling logic"""
        # Does the previous bettor have me covered?
        am_covered = amount_to_call >= player.chips
        # Can I min raise with chips to spare?
        can_raise_with_surplus = amount_to_call + min_raise < player.chips


        is_bet_check = (not prev_bet_exists) or (player.amount_in == prev_highest_bet)
        is_raise_call = prev_bet_exists and (player.amount_in != prev_highest_bet)

        only_all_in_bet = (not prev_bet_exists) and (not can_afford_min_bet)
        only_all_in_call = prev_bet_exists and am_covered
        only_all_in_raise = prev_bet_exists and (not can_raise_with_surplus)

        bet_or_raise = "bet" if is_bet_check else "raise"
        check_or_call = "check" if is_bet_check else "call"

        bet_all_in = "(all in)" if only_all_in_bet else ""
        call_all_in = "(all in)" if only_all_in_call else ""
        raise_all_in = "(all in)" if only_all_in_raise else ""

        bet_or_raise_all_in = bet_all_in or raise_all_in

        bet_or_raise_option = "" if call_all_in else f'''"{bet_or_raise} N" {bet_or_raise_all_in}\n\
Such that N is a number between {min_raise} and {player.chips}.\n'''
        ending = """Respond QUICKLY, with at most ONE word, and NO punctuation!"""

        p = player.personality

        return f"""\n{player.name}? It's your turn to act.\n\n\
You've been dealt {player.hole_cards}.\n\
There's ${round.pot.amount} in the pot.\n\
You have ${player.chips} in chips.\n\
\nAs {player.name}, you are {p.traits}. \
Your No-Limit Hold 'Em playstyle is {p.style}. \
This table has a strict time limit, so move quickly or be penalized.\n\n\
Choose from the following responses:
"{check_or_call}" {call_all_in}
"fold"
{bet_or_raise_option}
{ending}"""


def build_log(round: HoldemRound, perspective: Player | None = None) -> str:
    log_string = ""
    prev_phase = ""
    actions = round.actions

    prev_action_word = ""

    for action in actions:
        # Headers
        if(action.phase != prev_phase):
            log_string += f"\n\n{action.phase.upper()}\n\n"
        
        # Whitespace between actions of different types on game start.
        if (action.phase == Phases.GAME_START) and (prev_action_word != "") and (action.action != prev_action_word):
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

def log_action(round: HoldemRound, phase: str, subject: str, action: str, object: str="", subject_id=-1) -> HoldemRound:
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
            f"${player.chips} – {player.name}", 
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

    updated_player = update(player, chips=updated_chips, amount_in=updated_amount_in, is_all_in=updated_is_all_in)

    round = update_player(round, updated_player)
    round = update_pot(round, actual_bet)

    object = f"${updated_amount_in}"
    if(action == Actions.POST):
        object += " blind"

    return round

def post_blinds(round: HoldemRound) -> HoldemRound:

    # Post blinds.
    sb = HoldemRound.SMALL_BLIND
    bb = HoldemRound.BIG_BLIND
    play_round

    sb_id = -1
    bb_id = -1
    for player in round.players.values():
        if (player.position == "SB") or (len(round.players) == 2 and player.position == "BTN"):
            sb_id = player.player_id
        elif (player.position == "BB"):
            bb_id = player.player_id

    round = attempt_bet(round, round.players[sb_id], sb, Actions.POST)
    log_action(round, Phases.GAME_START, round.players[sb_id], Actions.POST, object=f"${sb}", subject_id=sb_id)
    round = attempt_bet(round, round.players[bb_id], bb, Actions.POST)
    log_action(round, Phases.GAME_START, round.players[bb_id], Actions.POST, object=f"${bb}", subject_id=bb_id)



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

def remove_node(round: HoldemRound, player: Player) -> HoldemRound:
    seen = set([player])

    players = round.players

    orphan_id = player.next_id_to_act
    orphan = players[orphan_id]

    current_player = orphan
    parent_candidate = current_player
    
    while current_player not in seen:
        parent_candidate = current_player
        seen.add(parent_candidate)

        next_id = parent_candidate.next_id_to_act
        current_player = players[next_id]
    

    new_parent = update(parent_candidate, next_id_to_act=orphan_id)
    inactive_node = update(player, next_id_to_act=-1)

    round = update_player(round, new_parent)
    round = update_player(round, inactive_node)

    return round



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

    # Flush players' amounts in at the beginning of each street.
    updated_players = {}
    for player in round.players.values():
        id = player.player_id
        if player in active_players:
            updated_players[id] = update(player, amount_in=0)
            continue
        updated_players[id] = player
    round = update(round, players=updated_players)


    # Get players by position.

    players_by_position = {}

    for player in total_players:
        players_by_position[player.position] = player
    
    # Big blind ends action preflop.
    last_to_act = players_by_position[Positions.BB]
    
    # Btn ends action all other streets.
    if phase != Phases.PREFLOP:
        last_to_act = players_by_position[Positions.BTN]
        # If BTN has folded we must find the nearest active player.
        ppp = HoldemRound.POSITIONS_PER_PLAYERCOUNT[len(total_players)]
        ppp_index = ppp.index(Positions.BTN) # Always 0
        while(last_to_act not in active_players):
            ppp_index -= 1
            prev_position = ppp[ppp_index]
            last_to_act = players_by_position[prev_position]

    first_id = last_to_act.next_id_to_act
    current_player = round.players[first_id]

    acted = set() # Flush this each time a player bets.

    highest_bet = 0 if not is_preflop else HoldemRound.BIG_BLIND
    min_raise = HoldemRound.BIG_BLIND

    starting_active_ids = set([player.player_id for player in active_players])
    folded_ids = set()

    while(current_player.player_id not in acted):

        # Skip all-in and folded players
        if(current_player.is_all_in or current_player.has_folded):
            print(f"Warning. This child ({current_player.name}) should have been severed.")
            next_id = current_player.next_id_to_act
            next_player = round.players[next_id]
            print(f"Attempting to continue with {next_player}.")
            current_player = next_player
            continue


        # Check if everyone else has folded.
        if(len(set.difference(starting_active_ids, folded_ids)) == 1):
            return round


        log = build_log(round, current_player)
        prompt = build_prompt(round, current_player, bet_occurred, highest_bet, min_raise)
        context = log + prompt

        print(f"\n\n\n{context}\n")

        client = anthropic.Anthropic()
        message = client.messages.create(
            # claude-opus-4-6 -> ~$0.10/min
            model="claude-haiku-4-5",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": context,
                }
            ],
        )
        response = message.content[0].text

        print(f"\n\n\nRESPONSE: {response}\n\n\n")
        processed = response.strip().lower().replace('*', '').replace('"', '') # AI bookend shit in ** sometimes.


        # If they didn't follow instructions, split it by \n\n and prune all but the last instance.
        if(len(processed) > 11):
            processed = processed.split('\n\n')[-1]

        action = ""
        bet_amount = 0
        has_folded = False
        is_all_in = False
        if(Actions.BET in processed):
            action = Actions.BET
            bet_amount = int(processed.split()[-1])
            acted = set([current_player.player_id]) # Everyone but this player needs to act again.
            round = log_action(round, phase, current_player, action, object=f"${bet_amount}", subject_id=current_player.player_id)

        elif(Actions.RAISE in processed):
            action = Actions.RAISE
            has_number = False
            for i in '1234567890':
                if i in processed:
                    has_number = True
                    break
            raise_by = int(processed.split()[-1]) if has_number else min_raise
            bet_amount = highest_bet + raise_by - current_player.amount_in
            acted = set([current_player.player_id]) # Everyone but this player needs to act again.
            round = log_action(round, phase, current_player, action, object=f"${bet_amount}", subject_id=current_player.player_id)

        elif (Actions.CALL in processed):
            # Keep this in for now, for when call unexpectedly fails to yield an all-in...
            print(f"DEBUGGING: attempt_bet({current_player.chips}, {highest_bet} - {current_player.amount_in})")
            action = Actions.CALL
            bet_amount = highest_bet - current_player.amount_in
            round = log_action(round, phase, current_player, action, subject_id=current_player.player_id)

        elif ("check" in processed):
            action = Actions.CHECK
            bet_amount = 0
            round = log_action(round, phase, current_player, action, subject_id=current_player.player_id)

        else:
            action = Actions.FOLD
            has_folded = True
            bet_amount = 0
            round = log_action(round, phase, current_player, action, subject_id=current_player.player_id)
            folded_ids.add(current_player.player_id)

        if(bet_amount == current_player.chips):
            current_player = update(current_player, is_all_in=True)

        if(bet_amount != 0):
            round = attempt_bet(round, current_player, bet_amount, action)

        current_player = update(current_player, amount_in=bet_amount, has_folded=has_folded, is_all_in=is_all_in)
        round = update_player(round, current_player)
        acted.add(current_player.player_id)


        next_id = current_player.next_id_to_act

        if(current_player.is_all_in or current_player.has_folded):
            round = remove_node(round, current_player)

        current_player = round.players[next_id]
    return round

def find_winners(round: HoldemRound, phase) -> list[Player]:
    is_showdown = phase == Phases.SHOWDOWN
    folded_count = sum([1 for p in round.players.values() if p.has_folded])

    if (not is_showdown) and (folded_count < len(round.players.values()) - 1):
        return []
    elif (not is_showdown) and (folded_count == len(round.players.values()) - 1):
        return [p for p in round.players.values() if not p.has_folded]

def settle_pot(round: HoldemRound, phase: str, winners: list[Player]):
    pot = round.pot
    while(pot != None):
        # TODO: Figure out the logic of side pots.
        amount_per_winner = pot.amount/len(winners)
        for player in winners:
            player = update(player, chips=player.chips + amount_per_winner)
            update_player(round, player)
            round = log_action(round, phase, player.name, Actions.COLLECT, str(amount_per_winner), player.player_id)
        pot = pot.parent_pot
    return round

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

    winners = find_winners(round, Phases.PREFLOP)
    if len(winners) != 0:
        round = settle_pot(round, Phases.PREFLOP, winners)
        return round

    # FLOP

    deck, community_cards = Deck.pop(deck, 3)
    round = update(round, community_cards=community_cards)
    round = log_action(round, Phases.FLOP, "Dealer", Actions.SHOW, str(community_cards))
    round = play_street(round, Phases.FLOP)

    winners = find_winners(round, Phases.FLOP)
    if len(winners) != 0:
        round = settle_pot(round, Phases.FLOP, winners)
        return round
    
    # TURN

    deck, turn_card = Deck.pop(deck, 1)
    round = log_action(round, Phases.TURN, "Dealer", Actions.TURN, f"{community_cards} [{turn_card}]")
    community_cards += turn_card
    round = update(round, community_cards=community_cards)
    round = play_street(round, Phases.TURN)

    winners = find_winners(round, Phases.TURN)
    if len(winners) != 0:
        round = settle_pot(round, Phases.TURN, winners)
        return round

    # RIVER

    deck, river_card = Deck.pop(deck, 1)
    round = log_action(round, Phases.TURN, "Dealer", Actions.TURN, f"{community_cards} [{river_card}]")
    community_cards += river_card
    round = update(round, community_cards=community_cards)
    round = play_street(round, Phases.RIVER)

    # TODO: Win conditions for showdown

    log_string = build_log(round)
    print(log_string)
    return round



