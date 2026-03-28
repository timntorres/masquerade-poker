
from game_structs import HoldemRound, Action, Player, Snapshot, T, Pot
from constants import Phases, Actions, Positions, Subjects
from deck import Deck, Hand, Card
from utils import init_rand, shuffle, get_time, update

import anthropic

import random
import math
round_ = round # fml for naming the HoldemRound instance round
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
        ending = """Respond QUICKLY, with at most ONE word and ONE number, and NO punctuation!"""

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
        pot=round.pot, 
        community_cards=round.community_cards, 
        players=round.players, 
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
            amount_in=0, 
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

def update_pot(round: HoldemRound, amount_to_add: float) -> HoldemRound:
    updated_pot = update(round.pot, amount=round.pot.amount + amount_to_add)
    return update(round, pot=updated_pot)

def attempt_bet(round: HoldemRound, player: Player, attempted_amount: int, action: str) -> HoldemRound:
    actual_bet = min(attempted_amount, player.chips)
    updated_chips = player.chips - actual_bet
    updated_amount_in = player.amount_in + actual_bet
    updated_is_all_in = (updated_chips == 0)

    updated_player = update(player, chips=updated_chips, amount_in=updated_amount_in, is_all_in=updated_is_all_in)

    round = update_players(round, [updated_player])
    round = update_pot(round, actual_bet)

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


        bet_amount = 0
        has_folded = False
        is_all_in = False
        if(Actions.BET in processed):
            action = Actions.BET
            bet_amount = value
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player, folded players, and all-in players need to act again.

        elif(Actions.RAISE in processed):
            action = Actions.RAISE
            raise_by = max(value, min_raise)
            bet_amount = highest_bet + raise_by - player.amount_in
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player needs to act again.

        elif (Actions.CALL in processed):
            # Keep this in for now, for when call unexpectedly fails to yield an all-in...
            action = Actions.CALL
            bet_amount = highest_bet - player.amount_in

        elif ("check" in processed):
            action = Actions.CHECK
            bet_amount = 0

        else:
            action = Actions.FOLD
            has_folded = True
            bet_amount = 0

            player = update(player, has_folded=True)
            round = update_players(round, [player])
            # Remove player from pot.
            pot_player_ids_copy = round.pot.player_ids

            pot_player_ids_copy.remove(player.player_id)
            pot = update(round.pot, player_ids=pot_player_ids_copy)
            round = update(round, pot=pot)
            folded_ids.add(player.player_id)

        if(bet_amount > 0):
            round, bet_amount = attempt_bet(round, player, bet_amount, action)
        player = round.players[curr_id]

        acted.add(player.player_id)

        highest_bet = max(highest_bet, player.amount_in)

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
            typed_object=bet_amount, 
            subject_id=player.player_id
            )

        curr_id = next_id
    return round

def has_folded_out_(round: HoldemRound) -> bool:
    phase = round.phase
    is_showdown = phase == Phases.SHOWDOWN
    remaining = sum([1 for p in round.players.values() if not p.has_folded])
    return (remaining == 1)
    

def settle_pot(round: HoldemRound, folded_out=False):
    pot = round.pot

    if(folded_out):
        winner = [p for p in round.players.values() if not p.has_folded]
        player = winner[0]
        player = update(player, chips=player.chips + pot.amount)
        update_players(round, [player])
        round = log_action(
            round=round,
            action=Actions.COLLECT,
            typed_object=pot.amount,
            subject_id=player.player_id
        )
        return round


    iteration = 0
    shown_players = set()
    while(pot != None):
        # TODO: Figure out the logic of side pots.
        candidates = [round.players[id] for id in pot.player_ids]
        winning_hands = Hand.find_winners(candidates, round.community_cards)

        amount_per_winner = round_(pot.amount/len(winning_hands), 2)

        for hand in winning_hands:
            player = hand.player

            if(player.player_id in shown_players):
                # Skip players who already won a pot, when side pot exists.
                continue

            shown_players.add(player.player_id)

            round = log_action( \
                round=round,
                action=Actions.SHOW,
                typed_object=player.hole_cards,
                object=f"{player.hole_cards} ({hand.hand_id})",
                subject_id=player.player_id
            )

        for hand in winning_hands:
            action = Actions.COLLECT if (iteration == 0) else Actions.COLLECT_SIDE
            player = hand.player
            player = update(player, chips=player.chips + amount_per_winner)
            update_players(round, [player])
            round = log_action(
                round=round,
                action=action,
                typed_object=amount_per_winner,
                subject_id=player.player_id
            )

        pot = pot.parent_pot
        iteration += 1
        round = update(round, pot=pot)
    return round

def play_round(round: HoldemRound) -> HoldemRound:
    # Shuffle deck.
    round = update(round, phase=Phases.GAME_START)
    round = init_rand(round)
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

        has_folded = has_folded_out_(round)

        if(has_folded):
            round = update(round, phase=Phases.RESULT)
            round = settle_pot(round, folded_out=True)
    
        return round, deck, has_folded

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
    
    
    log_string = build_log(round)
    print(log_string)
    return round



