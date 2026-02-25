from deck import Deck, Hand
from ollama import chat, Client
from rand_manager import shuffle, init_rand
import os
import yaml

class Personality:
    def __init__(self, name, traits, playstyle, quotes):
        self.name = name
        self.traits = traits
        self.playstyle = playstyle
        self.quotes = quotes

    @staticmethod
    def load_personalities(filename):
        with open(filename, 'r') as file:
            try:
                data = yaml.safe_load(file)
                characters = data['characters']
                personalities = []
                for character in characters:
                    p = Personality(
                        character['name'],
                        character['traits'],
                        character['playstyle'],
                        character['quotes']
                    )
                    personalities.append(p)
                return personalities
            except yaml.YAMLError as exc:
                print(exc)
                exit()
class Player:
    def __init__(self, name, buy_in, personality=None):
        self.name = name
        self.chips = buy_in
        self.hole_cards = []
        self.position = ""
        self.is_active = True
        self.all_in = False
        self.hand_number = 0
        self.hand_amount_in = 0
        self.street_amount_in = 0
        self.personality = personality
        self.has_personality = (personality is not None)

    def __str__(self):
        return f"{self.position}: {self.name} (${self.chips}) in for ${self.hand_amount_in} with {self.hole_cards}"
    
    __repr__ = __str__

    def init_round(self):
        self.is_active = True
        self.all_in = False
        self.hand_amount_in = 0
        self.street_amount_in = 0
        self.hand_number += 1


    @staticmethod
    def init_players(personalities, buy_in):
        players = []
        for personality in personalities:
            p = Player(
                personality.name,
                buy_in,
                personality
            )
            players.append(p)
        return players

    def build_local_context(self, pot, bet_occurred_this_street, prev_highest_street_amount_in, min_raise):
        # TODO: When everyone else is all in, and current player is stack leader, prevent that player from raising.
        """
        CASES
        1. bet, check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind? (self.chips > min_raise)
                Yes
        2. bet (all in), check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind? (self.chips > min_raise)
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

        prev_highest_bet = prev_highest_street_amount_in
        amount_to_call = prev_highest_bet - self.street_amount_in
        """Betting / Checking logic"""
        # Has anyone else bet this street?
        prev_bet_exists = bet_occurred_this_street
        # Can I afford to bet more than the minimum bet?
        can_afford_min_bet = self.chips > min_raise
        """Raising / Calling logic"""
        # Does the previous bettor have me covered?
        am_covered = amount_to_call >= self.chips
        # Can I min raise with chips to spare?
        can_raise_with_surplus = amount_to_call + min_raise < self.chips


        is_bet_check = (not prev_bet_exists) or (self.street_amount_in == prev_highest_bet)
        is_raise_call = prev_bet_exists and (self.street_amount_in != prev_highest_bet)

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
Such that N is a number between {min_raise} and {self.chips}.\n'''
        ending = """Respond QUICKLY, with at most ONE word, and NO punctuation!"""

        p = self.personality

        return f"""\n{self.name}? It's your turn to act.\n\n\
You've been dealt {self.hole_cards}.\n\
There's ${pot} in the pot.\n\
You have ${self.chips} in chips.\n\
\nAs {self.name}, you are {p.traits}. \
Your No-Limit Hold 'Em playstyle is {p.playstyle}. \
It's your {self.hand_number}th hand at this table with a strict time limit, so move quickly or be penalized.\n\n\
Choose from the following responses:
"{check_or_call}" {call_all_in}
"fold"
{bet_or_raise_option}"""

    def act(self, pot, community_context, prev_highest_street_amount_in, bet_occurred_this_street, min_raise):

        total_context = community_context + self.build_local_context(pot, bet_occurred_this_street, prev_highest_street_amount_in, min_raise)

        print(f"\n\n\n{total_context}\n\n\n")

        # glm-4.7-flash for local, but slow
        """
        response = chat(model='glm-4.7-flash', messages=[
        {
            'role': 'user',
            'content': total_context,
        },
        ])
        print(response.message.content)
        processed = response.message.content.strip().lower().replace('*', '')
        """

        client = Client(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
        )
        messages = [
        {
            'role': 'user',
            'content': total_context,
        },
        ]
        
        response = ""
        for part in client.chat('gpt-oss:20b-cloud', messages=messages, stream=True):
            print(part['message']['content'], end='', flush=True)
            response += part['message']['content']

        processed = response.strip().lower().replace('*', '') # AI bookend shit in ** sometimes.
        

        # If they didn't follow instructions, split it by \n\n and prune all but the last instance.
        if(len(processed) > 11):
            processed = processed.split('\n\n')[-1]

        if("bet" in processed):
            action = "bet"
            bet_amount = int(processed.split()[-1])
            self.chips, final_amount = Player.attempt_bet(self.chips, bet_amount)
        elif("raise" in processed):
            action = "raise"
            raise_amount = int(processed.split()[-1])
            self.chips, final_amount = Player.attempt_bet(self.chips, prev_highest_street_amount_in + raise_amount - self.street_amount_in)
        elif ("call" in processed):
            action = "call"
            # Keep this in for now, for when call unexpectedly fails to yield an all-in...
            print(f"DEBUGGING: attempt_bet({self.chips}, {prev_highest_street_amount_in} - {self.street_amount_in})")
            self.chips, final_amount = Player.attempt_bet(self.chips, prev_highest_street_amount_in - self.street_amount_in)
        elif ("check" in processed):
            action = "check"
            final_amount = 0
        else:
            action = "fold"
            self.is_active = False
            final_amount = 0
        # Keep this in for now, for when call unexpectedly fails to yield an all-in...
        print(f"DEBUGGING: ${self.chips} (self.chips)")
        if(self.chips == 0):
            self.all_in = True
        self.hand_amount_in += final_amount
        self.street_amount_in += final_amount
        return action, final_amount

    @staticmethod
    def attempt_bet(chips, amount):
        actual_bet = min(amount, chips)
        chips -= actual_bet
        return chips, actual_bet

    def post_blind(self, amount):
        self.chips, final_amount = Player.attempt_bet(self.chips, amount)
        if(self.chips == 0):
            self.all_in = True
        self.street_amount_in = final_amount
        self.hand_amount_in = final_amount
        return final_amount
        
"""
    Don't forget me when we hit the ground
    You and me against the dying of the light
"""

class TexasHoldEm:

    SMALL_BLIND = 1
    BIG_BLIND = 2
    MAX_BUY_IN = 30

    POSITIONS_PER_PLAYERCOUNT = \
        {
            2: ["BTN", "BB"],
            3: ["BTN", "SB", "BB"],
            4: ["BTN", "SB", "BB", "CO"],
            5: ["BTN", "SB", "BB", "HJ", "CO"],
            6: ["BTN", "SB", "BB", "UTG", "HJ", "CO"],
        }

    @staticmethod
    def find_last_to_act_postflop(remaining, postflop=True):
        # The BTN, or the person to the left of the BTN.
        scores = {"SB": 0, "BB": 1, "UTG": 2, "HJ": 3, "CO": 4, "BTN": 5}
        return max(remaining, key = lambda player: scores[player.position])
    
    @staticmethod
    def end_street(game_log, remaining_players, pot, deck, cards_to_pop=0):
        if(len(remaining_players) == 1):
            game_log += f"{remaining_players[0].name} collects ${pot} from the pot.\n"
            remaining_players[0].chips += pot
            return game_log, remaining_players, pot, deck, []

        # Flushing amount_in between streets
        for player in remaining_players:
            player.street_amount_in = 0

        # Showing cards when everyone's all in.
        amount_still_betting = 0
        shown_message = '\n'
        for player in remaining_players:
            shown_message += f"{player.name} shows {player.hole_cards}.\n"
            if(not player.all_in):
                amount_still_betting += 1
        if (amount_still_betting <= 1) and (shown_message not in game_log):
            game_log += shown_message

        # Next street's cards.
        popped_cards = []
        if(cards_to_pop > 0):
            deck, popped_cards = Deck.pop(deck, cards_to_pop)
        return game_log, remaining_players, pot, deck, popped_cards



    @staticmethod 
    def request_actions(round_name, big_blind_size, game_log, default_last_to_act, betting_players, pot, community_current=None, community_new=None):

        game_log += f"\n{round_name}:"

        bet_occurred_this_street = False
        if(round_name == 'PREFLOP'):
            bet_occurred_this_street = True

        if community_current is not None:
            game_log += f" {community_current}"
        if community_new is not None:
            game_log += f" {community_new}"
        game_log += "\n\n"

        # Try to skip action.
        players_in = 0
        for player in betting_players:
            if (not player.all_in):
                players_in += 1
        if(players_in <= 1):
            # TODO: Disambiguate betting players from showdown players.
            return game_log, betting_players, pot

        # Bet, call, or fold.
        # First to act is to the left of big blind.
        action_ends = False
        # print(betting_players)
        # print(default_last_to_act)
        default_lta_index = betting_players.index(default_last_to_act)

        i = (default_lta_index + 1)%len(betting_players)
        last_to_act = default_last_to_act
        folded = set()
        playerset = set(betting_players)
        prev_actor = last_to_act

        prev_highest_street_amount_in = big_blind_size
        min_raise = prev_highest_street_amount_in

        all_in_players = set()

        while not action_ends:

            player = betting_players[i]

            if player in folded:
                i += 1
                i %= len(betting_players)
                continue

            if player.all_in:
                i += 1
                i %= len(betting_players)
                all_in_players.add(player)
                # In case everyone's all in.
                if (player == last_to_act):

                    didnt_fold = []

                    for player in betting_players:
                        if player in folded:
                            continue
                        didnt_fold.append(player)

                    return game_log, didnt_fold, pot

                continue

            action, bet_size = player.act(pot, game_log, prev_highest_street_amount_in, bet_occurred_this_street, min_raise)

            pot += bet_size
            
            game_log += f"{player.name} {action}s"
           

            if action == 'bet':
                bet_occurred_this_street = True
                game_log += f" ${bet_size}"
                min_raise = bet_size
                prev_highest_street_amount_in = bet_size
                last_to_act = prev_actor
            if action == 'raise':
                bet_occurred_this_street = True
                game_log += f" to ${player.street_amount_in}"
                min_raise = player.street_amount_in - prev_highest_street_amount_in
                prev_highest_street_amount_in = player.street_amount_in
                last_to_act = prev_actor

            if player.all_in:
                game_log += f" and is all-in"

            game_log += ".\n"


            if action == "fold":
                folded.add(player)
            else:
                prev_actor = player

            everyone_folded = (len(folded) == len(betting_players) - 1)
            
            did_bet = (action == "raise") or (action == "bet")
            pot_is_right = (player == last_to_act and (not did_bet))
            if(everyone_folded or pot_is_right):
                print(f"\nEveryone folded? {everyone_folded}. Pot's right? {pot_is_right}.\n")
                action_ends = True

            i += 1
            i %= len(betting_players)

        didnt_fold = []

        for player in betting_players:
            if player in folded:
                continue
            didnt_fold.append(player)
            
        return game_log, didnt_fold, pot 

    def __init__(self):
        self.pot = 0
        self.highest_bet = 0
        self.deck = []
        self.players = []
        self.player_index_of_button = -1
        self.game_log = ''

    def add_players(self, game_log, options):
        options = shuffle(options)
        for i in range(6):
            self.players.append(players[i])
            self.game_log += f"{players[i].name} buys in for ${players[i].chips}.\n"
        return game_log

    def add_player(self, name, buy_in):
        if len(self.players) >= 6:
            return None
        new_player = Player(name, buy_in)
        self.players.append(new_player)
        self.game_log += f"{name} buys in for ${buy_in}.\n"
    
    def start_round(self, game_log="", round_number=0):
        self.pot = 0
        self.player_index_of_button += 1
        self.player_index_of_button %= len(self.players)
        for player in self.players:
            player.init_round()

        if(len(self.players) <= 1): 
            print(f"{len(self.players)} player(s) isn't enough to play poker.")
            return game_log

        self.game_log = game_log
    
        self.deck = shuffle(Deck.generate_deck())

        # Print metadata
        self.game_log += f"\nStarting hand #{round_number}.\n\n"
        # Set positions.
        position_names = TexasHoldEm.POSITIONS_PER_PLAYERCOUNT[len(self.players)]
        # Post blinds.
        sb = 0
        bb = 0
        sb_name = ''
        bb_name = ''
        bb_index = self.player_index_of_button - 1
        for index, player in enumerate(self.players):
            player.position = position_names[index - self.player_index_of_button]
            if (player.position == "SB") or (len(self.players) == 2 and player.position == "BTN"):
                sb = player.post_blind(TexasHoldEm.SMALL_BLIND)
                sb_name = player.name
            elif (player.position == "BB"):
                bb = player.post_blind(TexasHoldEm.BIG_BLIND)
                bb_name = player.name
                bb_index = index
            else:
                player.street_amount_in = 0
        self.game_log += f"{sb_name} posts small blind (${sb}).\n"
        self.game_log += f"{bb_name} posts big blind (${bb}).\n\n"
        # Add chips here
        self.pot += sb
        self.pot += bb
        # Distribute hole cards.
        for index, player in enumerate(self.players):
            self.deck, player.hole_cards = Deck.pop(self.deck, 2)
            self.game_log += f"Dealt two cards to {player.position}, {player.name} (${player.chips}).\n"

        remaining_players = []

        # PREFLOP

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("PREFLOP", self.BIG_BLIND, self.game_log, self.players[bb_index], self.players, self.pot)

        self.game_log, remaining_players, self.pot, self.deck, flop_cards = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 3)

        if(len(remaining_players) == 1):
            return self.game_log


        # FLOP

        last = TexasHoldEm.find_last_to_act_postflop(remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("FLOP", self.BIG_BLIND, self.game_log, last, remaining_players, self.pot, community_new=flop_cards)

        self.game_log, remaining_players, self.pot, self.deck, turn_card = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 1)

        if(len(remaining_players) == 1):
            return self.game_log

        # TURN

        last = TexasHoldEm.find_last_to_act_postflop(remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("TURN", self.BIG_BLIND, self.game_log, last, remaining_players, self.pot, community_current=flop_cards, community_new=turn_card)

        self.game_log, remaining_players, self.pot, self.deck, river_card = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 1)

        if(len(remaining_players) == 1):
            return self.game_log


        # RIVER

        last = TexasHoldEm.find_last_to_act_postflop(remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("RIVER", self.BIG_BLIND, self.game_log, last, remaining_players, self.pot, community_current=flop_cards + turn_card, community_new=river_card)
        
        self.game_log, remaining_players, self.pot, self.deck, disregard = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck)

        if(len(remaining_players) == 1):
            return self.game_log
        winners = Hand.find_winners(remaining_players, flop_cards + turn_card + river_card)

        s = ''
        if(len(winners) > 1):
            s = 's'
        self.game_log += f"Winner{s}: "
        portion = self.pot/len(winners)
        winner_set = set([winner.player.name for winner in winners])
        for winner in winners:
            self.game_log += winner.player.name
            self.game_log += f" showed {winner.player.hole_cards} ({winner.hand_id}) and collects ${portion}.\n"

        self.game_log += "\n"


        pruned_players = []
        for player in self.players:
            # Limitation: requires players' names to be unique.
            if(player.name in winner_set):
                player.chips += portion
            # Kick out players with 0 chips.
            if(player.chips == 0):
                self.game_log += f"{player.name} leaves the table.\n"
                continue
            pruned_players.append(player)
        self.players = pruned_players

        
        return self.game_log


if __name__ == "__main__":
    init_rand()
    # seed=1772015243803030
    

    personalities = Personality.load_personalities('characters.yaml')
    players = Player.init_players(personalities, TexasHoldEm.MAX_BUY_IN)

    t = TexasHoldEm()
    game_log = ""

    game_log = t.add_players(game_log, players)

    i = 0
    game_log = ''
    while len(t.players) > 1:
        game_log = init_rand()
        game_log += t.start_round(game_log, i)
        i += 1

    game_log += f"\n\n{t.players[0].name} won."