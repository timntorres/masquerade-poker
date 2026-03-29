
from game_structs import HoldemRound, Action, Player, Snapshot, T, Pot, PotQueue
from constants import Phases, Actions, Positions, Subjects
from deck import Deck, Hand, Card
from utils import init_rand, shuffle, get_time, update

import anthropic

import random
import math
round_ = round # fml for naming the HoldemRound instance round
import time
import copy

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
        amount_to_call = prev_highest_bet - player.amount_in_street
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


        is_bet_check = (not prev_bet_exists) or (player.amount_in_street == prev_highest_bet)

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
Such that N is a number between {min_raise} and {player.chips - prev_highest_bet}.\n'''
        ending = """Respond QUICKLY, with at most ONE word and ONE number, and NO punctuation!"""

        p = player.personality

        return f"""\n{player.name}? It's your turn to act.\n\n\
You've been dealt {player.hole_cards}.\n\
There's ${round.pot_queue.total_amount} in the pot.\n\
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

    headers = set()

    for action in actions:
        phase = action.snapshot.phase
        round_id = action.snapshot.round_id
        subject_id = action.snapshot.subject_id
        # Headers
        header_string = f"{phase.value.upper()} (Hand #{round_id})"
        if(header_string not in headers):
            log_string += f"\n\n{header_string}\n\n"
            headers.add(header_string)

        
        # Whitespace between actions of different types on game start.
        if (phase == Phases.GAME_START) and (prev_action_word != "") and (action.action != prev_action_word):
            log_string += "\n"
        prev_action_word = action.action
        
        perspective_exists = perspective is not None
        perspective_differs = perspective_exists and (subject_id != perspective.player_id)
    
        must_anonymize = perspective_differs and (action.subject_type != Subjects.DEALER)
        if must_anonymize:
            action = Action.anonymize(action)
            
        log_string += f"{action}\n"
        action.action


        prev_phase = phase
    return log_string

def log_action(round: HoldemRound, action: str, typed_object: T, object: str | None = None, subject_id:str = Subjects.DEALER_ID) -> HoldemRound:

    if object == None:
        object = str(typed_object)

    subject_type = Subjects.DEALER
    subject = Subjects.DEALER

    if(subject_id != Subjects.DEALER_ID):
        subject_type=Subjects.PLAYER
        subject = round.players[subject_id].name


    snapshot = Snapshot(
        typed_object=typed_object, 
        phase=round.phase, 
        round_id=round.round_id,
        pot_queue=round.pot_queue,
        community_cards=copy.deepcopy(round.community_cards), 
        players=copy.deepcopy(round.players), 
        time=get_time(), 
        subject_id=subject_id
        )

    new_action = Action(
        subject_type=subject_type, 
        subject=subject, 
        action=action, 
        object=object, 
        snapshot=snapshot
        )

    action_list = round.actions
    action_list.append(new_action)

    return update(round, actions=action_list)

def init_rand(round, seed=None):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    random.seed(seed)
    round = log_action(round, Actions.SHUFFLE, seed)
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
            player_id=player.player_id,
            name=player.name, 
            position=Positions.NONE, 
            personality=player.personality, 
            hole_cards=[], 
            chips=player.chips, 
            amount_in_street=0, 
            amount_in_round=0,
            has_folded=False, 
            is_all_in=False,
            prev_id=-1,
            next_id=-1
        )
        updated_players[player.player_id] = updated_player
        # Populate updated player in same seat.
        seat_index = round.seats.index(player.player_id)
        updated_seats[seat_index] = updated_player.player_id
    

    return update(round, players=updated_players, seats=updated_seats)
    
def set_positions(round: HoldemRound) -> HoldemRound:
    round = update(round, seat_index_of_btn=(round.seat_index_of_btn + 1) % len(round.seats))

    position_names = HoldemRound.POSITIONS_PER_PLAYERCOUNT[len(round.players)]

    updated_players = {}

    # Find ID of btn
    btn_seat_index = round.seat_index_of_btn

    while round.seats[btn_seat_index] == -1:
        btn_seat_index +=1
        btn_seat_index %= len(round.seats)

    btn_id = round.seats[btn_seat_index]    
    btn_player = round.players[btn_id]


    players_in_seat_order = []

    for player_id in round.seats:
        # Seats can be empty.
        if(player_id == -1):
            continue
        players_in_seat_order.append(round.players[player_id])

    offset = players_in_seat_order.index(btn_player)

    for i in range(offset - len(players_in_seat_order), offset):
        player = players_in_seat_order[i]
        new_position = position_names[i - offset]
        new_next_id = players_in_seat_order[(i + 1)%len(players_in_seat_order)].player_id
        new_prev_id = players_in_seat_order[(i - 1)%len(players_in_seat_order)].player_id

        updated_players[player.player_id] = \
            update(player, position=new_position, next_id=new_next_id, prev_id=new_prev_id)
    round = update(round, players=updated_players)

    return update(round, players=updated_players)

def update_players(round: HoldemRound, players_to_update: list[Player]) -> HoldemRound:

    updated_players = round.players
    
    for player in players_to_update:
        updated_players[player.player_id] = player

    return update(round, players=updated_players)

def right_pot(round: HoldemRound) -> HoldemRound:

    pot_queue = round.pot_queue
    ids_to_bets = pot_queue.ids_to_bets
    right_pots = pot_queue.right_pots if len(pot_queue.right_pots) else (Pot({}, 0),)

    if(len(ids_to_bets) == 0):
        return round

    # At the end of each street, the dealer creates one side pot for each unique all-in stack size,
    # in order from smallest to largest. Each side pot contains the maximum number of chips that a
    # player of that stack size can win.
    
    # The remainder (shared by each person who bet the max bet size) goes into the main pot.
    # If the main pot has 1 player involved, then it's uncalled and will return to that player.
    # (This will be checked for at showdown.)

    # To right the pot, first we determine if a side pot must be created. 
    # Any of these two conditions may be met.

    # SIDE POT CONDITION 1. Same bet sizes among non-folded players
    # On all streets except showdown: Co-existence of all-in and non all-in players

    bet_sizes = [bet for bet in ids_to_bets.values()]
    unique_bet_sizes = set(bet_sizes)
    sorted_unique_bet_sizes = sorted(unique_bet_sizes)

    amount_this_street = sum(bet_sizes)

    non_folded_bet_sizes = [ids_to_bets[id] for id in ids_to_bets if not round.players[id].has_folded]
    unique_non_folded_bet_sizes = set(non_folded_bet_sizes)

    all_in_ids = []
    ids_in_action = []

    for player in round.players.values():
        if(player.is_all_in):
            all_in_ids.append(player.player_id)
            continue
        if(player.has_folded):
            continue
        ids_in_action.append(player.player_id)
    
    coexistence = len(all_in_ids) > 0 and len(ids_in_action) > 1 
    # ids_in_action > 1 because, e.g., one person with chips remaining has no more reason to bet.
    is_river = round.phase == Phases.RIVER
    condition_1_met = coexistence and (not is_river) # Last street means "chips left behind" no longer create side pots.
    all_same_bet_size = len(unique_non_folded_bet_sizes) == 1

    if all_same_bet_size:
        main_pot = right_pots[-1]
        main_pot = update(main_pot, ids_involved=ids_to_bets.keys(), amount=main_pot.amount + amount_this_street)

        tuple_to_concatenate = (main_pot,)
        if condition_1_met:
            # What we called the main pot, above, is now a side pot.
            actual_main_pot = Pot(set([id for id in ids_in_action]), 0)
            tuple_to_concatenate = tuple_to_concatenate + (actual_main_pot,)

        right_pots = right_pots[:-1] + tuple_to_concatenate
        pot_queue = update(pot_queue, right_pots=right_pots, ids_to_bets={})
        round = update(round, pot_queue=pot_queue)
        print("condition 1")
        print(ids_to_bets)
        print(right_pots)
        return round

    # SIDE POT CONDITION 2. Different bet sizes
    # The existence of differing non-folded bet sizes at street end implies that each smaller bet size must
    # belong to an all-in player and, therefore, must yield a side pot.

    copy_to_disburse = copy.copy(ids_to_bets) # Subtract from this one while iterating through the other one.

    # Create one side pot for each differing bet size with an all-in person in it.
    # TODO: Determine if the lowest side pot should update the values of the previous main pot?

    ids_removed = set()

    # EXAMPLE:
    # Iterating through bet sizes A, B, and C
    #
    #   A     B        C   
    # ##| <- P|ayer in |he blinds who folded
    # ##|#####| <- Shor|-stacked player who raised all-in 
    # ##|#####| <- Pers|n who called the all-in then folded to a 3-bet
    # ##|#####|########| <- Person who 3-bet
    # ##|#####|########| <- Stack leader cold-called
    #
    # Bet size A has the blind who folded.
    # Bet size B has one all-in and one caller who folded.
    # Bet size C has the two stack leaders.
    # 
    # So for every tier like A, where there's no one at that tier who's all-in,
    # we add it to dead money, then add dead money to the next eligible pot's tier.
    # 
    # i.e. For a side pot to be created at some bet size, there must be at least one 
    # player at that bet size who's all-in.

    main_pot = right_pots[-1]
    right_pots = right_pots[:-1]
    dead_money = main_pot.amount # add this to the next eligible pot

    for bet_size in sorted_unique_bet_sizes:

        bettors_of_this_size = [round.players[id] for id in ids_to_bets \
            if (ids_to_bets[id] == bet_size)]

        those_who_folded = [player for player in bettors_of_this_size \
            if player.has_folded]

        # Add this value (decremented by smaller bet sizes' side pots) 
        # for every player remaining in copy_to_disburse.
        id_of_a_bettor = bettors_of_this_size[0].player_id
        adjusted_amount = copy_to_disburse[id_of_a_bettor] # The equivalent of bet_size, but decremented.

        # Each player matches the covered player's stack.
        side_pot_size = len(copy_to_disburse.values()) * adjusted_amount + dead_money

        if len(those_who_folded) < len(bettors_of_this_size):
            side_pot = Pot(
                set(copy_to_disburse.keys()),
                side_pot_size
            )
            right_pots += (side_pot,)
            dead_money = 0
        else:
            # Accumulate this for the next valid side pot.
            dead_money = side_pot_size

        for id in ids_to_bets:
            # Remove bettors_of_this_size from copy_to_disburse.
            # They will no longer participate in any future pots.
            if(round.players[id] in bettors_of_this_size):
                copy_to_disburse.pop(id)
                ids_removed.add(id)
                continue

            # Skip lower-stacked players
            elif id in ids_removed:
                continue

            # Subtract the difference from every remaining player.
            copy_to_disburse[id] -= adjusted_amount

    pot_queue = update(pot_queue, right_pots=right_pots, ids_to_bets={})
    round = update(round, pot_queue=pot_queue)
    print("condition 2")
    print(ids_to_bets)
    print(right_pots)
    return round

def update_pot(round: HoldemRound, amount: float, bettor_id: int) -> HoldemRound:
    ids_to_bets = round.pot_queue.ids_to_bets

    prev_bet = ids_to_bets.setdefault(bettor_id, 0)
    ids_to_bets[bettor_id] = prev_bet + amount

    updated_pot_queue = update( \
        round.pot_queue,
        ids_to_bets=ids_to_bets,
        total_amount=round.pot_queue.total_amount + amount
        )
    return update(round, pot_queue=updated_pot_queue)

def attempt_bet(round: HoldemRound, player: Player, attempted_amount: int, action: str) -> HoldemRound:
    actual_bet = min(attempted_amount, player.chips)
    updated_chips = player.chips - actual_bet
    updated_amount_in_street = player.amount_in_street + actual_bet
    updated_amount_in_round = player.amount_in_round + actual_bet
    updated_is_all_in = (updated_chips == 0)

    updated_player = update( \
        player, chips=updated_chips, \
        amount_in_street=updated_amount_in_street, \
        amount_in_round=updated_amount_in_round, \
        is_all_in=updated_is_all_in)

    round = update_players(round, [updated_player])
    round = update_pot(round, actual_bet, player.player_id)

    return round, actual_bet

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

    round, sb_actual = attempt_bet(round, round.players[sb_id], sb, Actions.POST)
    round, bb_actual = attempt_bet(round, round.players[bb_id], bb, Actions.POST)

    for id in round.seats:
        if id == -1:
            continue
        p = round.players[id]
        position = p.position
        round = log_action(
            round=round,
            action=Actions.IS_POSITION,
            typed_object=position,
            subject_id=p.player_id
        )

    round = log_action(round=round, action=Actions.POST, typed_object=sb_actual, subject_id=sb_id)
    round = log_action(round=round, action=Actions.POST, typed_object=bb_actual, subject_id=bb_id)

    #If posting blinds made them all_in, we must remove their node
    if(round.players[sb_id].is_all_in):
        remove_node(round=round, player=round.players[sb_id])
    if(round.players[bb_id].is_all_in):
        remove_node(round=round, player=round.players[bb_id])



    return round

def get_player_id_by_position(round: HoldemRound, position: str) -> int:
    id = -1
    for player in round.players.values():
        if player.position == position:
            id = player.player_id
    return id


def deal_hole_cards(deck: Deck, round: HoldemRound) -> tuple[Deck, HoldemRound]:
    updated_players = round.players
    btn_id = get_player_id_by_position(round, Positions.BTN)
    current_id = round.players[btn_id].next_id
    ids_seen = set()

    while(current_id not in ids_seen):
        current_player = round.players[current_id]
        deck, hole_cards = Deck.pop(deck, 2)

        # Potential issue: These actions are being logged with outdated round instances
        updated_players[current_player.player_id] = update(current_player, hole_cards=hole_cards)
        round = log_action(round, Actions.DEALT, typed_object=hole_cards, subject_id=current_player.player_id)
        ids_seen.add(current_id)
        current_id = current_player.next_id

    round = update(round, players=updated_players)
    

    return deck, round

def remove_node(round: HoldemRound, player: Player) -> HoldemRound:

    my_id = player.player_id
    new_parent_id = player.prev_id
    new_child_id = player.next_id

    new_parent = update(round.players[new_parent_id], next_id=new_child_id)
    new_child = update(round.players[new_child_id], prev_id=new_parent_id)
    player = update(round.players[my_id], prev_id=-1, next_id=-1)

    round = update_players(round, [new_parent, new_child, player])

    return round

def interpret_response(response: str) -> tuple [str, float]:

    print(f"{response}")

    # If they didn't follow instructions, split it by \n\n and prune all but the last instance.
    if(len(response) > 15):
        response = response.split('\n\n')[-1]

    response = response.strip().lower().replace('*', '').replace('"', '')

    # Some models like replying with, say, "raise80" instead of "raise 80", 
    # so we need to split it by iterating backwards until we find the first non-number.
    val_string = ""
    digits = '1234567890'
    for i in range(len(response)):
        char = response[-1 - i]
        if char not in digits:
            break
        val_string = char + val_string
    
    response_string = response[: -1 * len(val_string)] if len(val_string) > 0 else response
    val = float(val_string) if val_string != "" else -1

    # Some models reply with "allin" or "all in".
    if("allin" in response_string) or ("all in" in response_string):
        response_string = "raise"
        val = math.inf

    return response_string, val

def request_action(round: HoldemRound) -> HoldemRound:
    phase = round.phase

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

    first_id = last_to_act.next_id
    curr_id = first_id

    acted = set() # Flush this each time a player bets.

    highest_bet = 0 if not is_preflop else HoldemRound.BIG_BLIND
    min_raise = HoldemRound.BIG_BLIND

    starting_active_ids = set([player.player_id for player in active_players])
    folded_ids = set()
    all_in_ids = set()

    while(curr_id not in acted):
        player = round.players[curr_id]
        # Skip all-in and folded players
        if(player.is_all_in or player.has_folded):
            print(f"Warning. This child ({player.name}) should have been severed.")
            next_id = player.next_id
            next_player = round.players[next_id]
            print(f"Attempting to continue with {next_player}.")
            player = next_player
            continue


        # Check if everyone else has folded.
        if(len(set.difference(starting_active_ids, folded_ids)) == 1):
            return round


        log = build_log(round, player)
        prompt = build_prompt(round, player, bet_occurred, highest_bet, min_raise)
        context = log + prompt

        print(f"\n\n\n{context}\n")

        client = anthropic.Anthropic()
        message = client.messages.create(
            # claude-opus-4-6 -> ~$0.10/min
            model="claude-haiku-4-5",
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": context,
                }
            ],
        )
        response = message.content[0].text

        processed, value = interpret_response(response)

                # processed = 'raise'
        # value = 99999


        bet_amount = 0

        if(Actions.BET in processed):
            action = Actions.BET
            bet_amount = value
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player, folded players, and all-in players need to act again.

        elif(Actions.RAISE in processed):
            action = Actions.RAISE
            raise_by = max(value, min_raise)
            bet_amount = highest_bet + raise_by - player.amount_in_street
            min_raise = raise_by
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player needs to act again.

        elif (Actions.CALL in processed):
            # Keep this in for now, for when call unexpectedly fails to yield an all-in...
            action = Actions.CALL
            bet_amount = highest_bet - player.amount_in_street

        elif ("check" in processed):
            action = Actions.CHECK
            bet_amount = 0

        else:
            action = Actions.FOLD
            bet_amount = 0

            player = update(player, has_folded=True)
            round = update_players(round, [player])
            folded_ids.add(player.player_id)

        if(bet_amount > 0):
            round, bet_amount = attempt_bet(round, player, bet_amount, action)
        player = round.players[curr_id]

        acted.add(player.player_id)

        highest_bet = max(highest_bet, player.amount_in_street)

        next_id = player.next_id

        if(player.is_all_in):
            all_in_ids.add(player.player_id)
            round = remove_node(round, player)
            

        if(player.has_folded):
            folded_ids.add(player.player_id)
            round = remove_node(round, player)

        round = log_action( \
            round=round, 
            action=action, 
            typed_object=bet_amount if action != Actions.RAISE else player.amount_in_street, 
            subject_id=player.player_id
            )

        print(f'{round.players[curr_id]} has ${player.chips} in chips left after the end of this action')
        curr_id = next_id

        stack_sanity_check(round)


    return round

def has_folded_out_(round: HoldemRound) -> bool:
    phase = round.phase
    is_showdown = phase == Phases.SHOWDOWN
    remaining = sum([1 for p in round.players.values() if not p.has_folded])
    return (remaining == 1)
    

def settle_pot(round: HoldemRound, folded_out=False):
    pot = round.pot_queue

    if(folded_out):
        winner = [p for p in round.players.values() if not p.has_folded]
        player = winner[0]
        player = update(player, chips=player.chips + pot.total_amount)
        round = update_players(round, [player])
        round = log_action(
            round=round,
            action=Actions.COLLECT,
            typed_object=pot.total_amount,
            subject_id=player.player_id
        )
        return round


    right_pots = pot.right_pots
    shown_ids = set()
    pot_number = -1
    first_pot_was_uncalled = False
    while(len(right_pots) > 0):
        pot_number += 1
        current_pot = right_pots[-1]
        right_pots = right_pots[:-1]

        candidates = [round.players[id] for id in current_pot.ids_involved \
            if not round.players[id].has_folded]

        if(len(candidates) == 1 and (pot_number == 0)):
            # Uncalled
            first_pot_was_uncalled = True

            if(current_pot.amount == 0):
                continue

            player = update(candidates[0], chips=candidates[0].chips + current_pot.amount)
            round = update_players(round, [player])
            round = log_action(round, Actions.RETURN, current_pot.amount, subject_id=candidates[0].player_id)
            continue

        winning_hands = Hand.find_winners(candidates, round.community_cards)
        amount_per_winner = current_pot.amount/len(winning_hands)
        
        for hand in winning_hands:
            player = hand.player
            if(player in shown_ids):
                continue
            player = hand.player
            round = log_action(round, Actions.SHOW, player.hole_cards, \
                    object=f"{player.hole_cards} ({hand.hand_id})", subject_id=player.player_id)
            shown_ids.add(player.player_id)
        
        for hand in winning_hands:
            player = hand.player
            player = update(player, chips=player.chips + amount_per_winner)
            round = update_players(round, [player])

            action = Actions.COLLECT_SIDE

            if (pot_number == 0 and (not first_pot_was_uncalled)) or \
            pot_number == 1 and first_pot_was_uncalled:
                action = Actions.COLLECT

            round = log_action(round, action, amount_per_winner, subject_id=player.player_id)
    return round

def remove_empty_stacks(round:HoldemRound) -> HoldemRound:
    updated_players = {}
    for player in round.players.values():
        if(player.chips == 0):
            round = log_action(round=round, action=Actions.EXIT, typed_object=None, subject_id=player.player_id)
            continue
        updated_players[player.player_id] = player
    return update(round, players=updated_players)

def stack_sanity_check(round: HoldemRound):
    sum = 0
    for player in round.players.values():
        sum += player.chips
    
    sum += round.pot_queue.total_amount
    expected = HoldemRound.MAX_BUY_IN*6
    if(sum == expected):
        return

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    log_string = build_log(round)
    print(log_string)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(f"Warning. Expected {expected} but got {sum}.")
    # exit()


def play_round(round: HoldemRound) -> HoldemRound:
    # Shuffle deck.
    round = update(round, phase=Phases.GAME_START)
    # seed=1774796861768377 <- good one for quick testing
    round = init_rand(round, seed=1774796861768377)
    button_index = 0
    round = refresh_players(round)
    deck = shuffle(Deck.generate_deck())
    round = set_positions(round)

    round = post_blinds(round)

    deck, round = deal_hole_cards(deck, round)

    def play_street(round: HoldemRound, deck:list[Card], phase:str, cards_to_pop:int) -> HoldemRound:
        community_cards=round.community_cards

        round = update(round, phase=phase)

        if(cards_to_pop != 0):
            deck, added_cards = Deck.pop(deck, cards_to_pop)
            community_cards += added_cards
            round = update(round, community_cards=community_cards)
            object = str(community_cards) if cards_to_pop != 1 else \
                f"{community_cards[:-1]} [{community_cards[-1]}]"
            round = log_action(round=round, action=Actions.FLIP, \
                typed_object=community_cards, object=object)

        round = request_action(round)

        # Flush players' amounts in at the end of each street.
        updated_players = {}
        for player in round.players.values():
            id = player.player_id
            updated_players[id] = update(player, amount_in_street=0)
            continue
        round = update(round, players=updated_players)

        has_folded_out = has_folded_out_(round)
        

        if has_folded_out:
            round = update(round, phase=Phases.RESULT)
            round = settle_pot(round, folded_out=True)

        round = right_pot(round)    

        return round, deck, has_folded_out

    round, deck, has_folded_out = play_street(round, deck, Phases.PREFLOP, cards_to_pop=0)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.FLOP, cards_to_pop=3)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.TURN, cards_to_pop=1)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.RIVER, cards_to_pop=1)
    if(has_folded_out): return round

    round = update(round, phase=Phases.SHOWDOWN)
    round = settle_pot(round, folded_out=False)
    
    round = remove_empty_stacks(round)

    
    log_string = build_log(round)
    print(log_string)
    return round



