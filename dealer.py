from deck import Deck, Hand
from ollama import chat

class Player:
    def __init__(self, name, buy_in):
        self.name = name
        self.chips = buy_in
        self.hole_cards = []
        self.is_active = True
        self.all_in = False
        self.position = ""
        self.hand_number = 0
        self.amount_in = 0

    def build_local_context(self, is_check, prev_highest_bet, min_raise):
        call_all_in = ""
        check_or_call = "call"
        if(is_check):
            check_or_call = "check"

        raise_is_an_option = prev_highest_bet - self.amount_in < self.chips

        ending = f""""raise N"
Such that N is a number between {min_raise} and {self.chips}.\n
Respond QUICKLY, with at most ONE word and ONE number, and NO punctuation!""" if min_raise < self.chips else f"""\"raise {self.chips}" (all in).\n
Respond QUICKLY, with at most ONE word and ONE number, and NO punctuation!"""

        if(not raise_is_an_option):
            call_all_in = " (all in)"
            ending = """\n
Respond QUICKLY, with at most ONE word, and NO punctuation!"""


        return f"""\nYour name is {self.name}. \
You are an expert at No-Limit Hold 'Em who makes extremely accurate decisions incredibly quickly. \
It's your {self.hand_number}th hand at this table with a strict time limit. Trust your instinct and make snap judgments. \
It's your turn to act. \n
You've been dealt {self.hole_cards}.\n\
You have {self.chips} in chips.\n
Choose from the following responses:
"{check_or_call}{call_all_in}"
"fold"
{ending}
"""

    def act(self, community_context, prev_highest_bet, min_raise):
        is_check = self.amount_in == prev_highest_bet

        total_context = community_context + self.build_local_context(is_check, prev_highest_bet, min_raise)

        print(f"\n\n\n{total_context}\n\n\n")

        response = chat(model='glm-4.7-flash', messages=[
        {
            'role': 'user',
            'content': total_context,
        },
        ])

        print(response.message.content)
        processed = response.message.content.strip().lower()

        # If they didn't follow instructions, split it by \n\n and prune all but the last instance.
        if(len(processed) > 11):
            processed = processed.split('\n\n')[-1]

        if("raise" in processed):
            action = "raise"
            raise_amount = int(processed.split()[-1])
            self.chips, final_amount = Player.attempt_bet(self.chips, prev_highest_bet + raise_amount - self.amount_in)
        elif ("call" in processed):
            action = "call"
            self.chips, final_amount = Player.attempt_bet(self.chips, prev_highest_bet - self.amount_in)
        elif ("check" in processed):
            action = "check"
            final_amount = 0
        else:
            action = "fold"
            self.is_active = False
            final_amount = 0

        if(self.chips == 0):
            self.all_in = True
        self.amount_in += final_amount
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
        self.amount_in = final_amount
        return final_amount
        
"""
    Don't forget me when we hit the ground
    You and me against the dying of the light
"""

class TexasHoldEm:

    SMALL_BLIND = 2
    BIG_BLIND = 5
    MAX_BUY_IN = 500

    POSITIONS_PER_PLAYERCOUNT = \
        {
            2: ["BTN", "BB"],
            3: ["BTN", "SB", "BB"],
            4: ["BTN", "SB", "BB", "CO"],
            5: ["BTN", "SB", "BB", "HJ", "CO"],
            6: ["BTN", "SB", "BB", "UTG", "HJ", "CO"],
        }

    @staticmethod
    def find_first_to_act_postflop(remaining, postflop=True):
        # The small blind, or the person to the right of the small blind.
        scores = {"SB": 0, "BB": 1, "UTG": 2, "HJ": 3, "CO": 4, "BTN": 5}
        return min(remaining, key = lambda player: scores[player.position])
    
    @staticmethod
    def end_street(game_log, remaining_players, pot, deck, cards_to_pop=0):
        if(len(remaining_players) == 1):
            game_log += f"{remaining_players[0]} collects ${pot} from the pot.\n"
            remaining_players[0].chips += pot
            return game_log, remaining_players, pot, deck, cards_to_pop

        game_log += f"\n"
        for player in remaining_players:
            game_log += f"{player.name} (${player.chips}) remains.\n"
        game_log += f"Pot: ${pot}"

        popped_cards = []
        if(cards_to_pop > 0):
            deck, popped_cards = Deck.pop(deck, cards_to_pop)

        return game_log, remaining_players, pot, deck, popped_cards



    @staticmethod 
    def request_actions(round_name, big_blind_size, game_log, default_last_to_act, betting_players, pot, community_current=None, community_new=None):
        game_log += f"\n{round_name}:"
        if community_current is not None:
            game_log += f" {community_current}"
        if community_new is not None:
            game_log += f" {community_new}"
        game_log += "\n\n"

        # Bet, call, or fold.
        # First to act is to the left of big blind.
        action_ends = False

        default_lta_index = betting_players.index(default_last_to_act)

        i = (default_lta_index + 1)%len(betting_players)
        last_to_act = default_last_to_act
        inactive = set()
        prev_actor = last_to_act

        prev_highest_bet = big_blind_size
        min_raise = prev_highest_bet

        all_in_players = set()

        while not action_ends:

            player = betting_players[i]

            if player in inactive:
                i += 1
                i %= len(betting_players)
                continue

            if player.all_in:
                i += 1
                i %= len(betting_players)
                all_in_players.add(player)
                # In case everyone's all in.
                if (player == last_to_act) and all_in_players == set(betting_players):
                    return game_log, didnt_fold, pot

                continue


            action, bet_size = player.act(game_log, prev_highest_bet, min_raise)

            game_log += f"{player.name} {action}s"
            if action == "raise":
                game_log += f" to ${player.amount_in}"
                min_raise = player.amount_in - prev_highest_bet
                prev_highest_bet = player.amount_in
                last_to_act = prev_actor

            if player.all_in:
                game_log += f" and is all-in"
            game_log += ".\n"
            
            if action == "fold":
                inactive.add(player)
            else:
                prev_actor = player

            everyone_folded = (len(inactive) == len(betting_players) - 1)
            
            pot_is_right = (player == last_to_act and action != "raise")
            if(everyone_folded or pot_is_right):
                print(f"Everyone folded? {everyone_folded}. Pot's right? {pot_is_right}.")
                action_ends = True

            i += 1
            i %= len(betting_players)

        didnt_fold = []

        for player in betting_players:
            if player in inactive:
                continue
            didnt_fold.append(player)
            
        return game_log, didnt_fold, pot 

    def __init__(self):
        self.pot = 0
        self.highest_bet = 0
        self.deck = []
        self.players = []
        self.player_index_of_button = 0
        self.game_log = ''

    def add_player(self, name, buy_in):
        if len(self.players) >= 6:
            return None
        new_player = Player(name, buy_in)
        self.players.append(new_player)
        self.game_log += f"{name} buys in for ${buy_in}.\n"
    
    def start_round(self, seed=None):
        self.deck = Deck.shuffle(Deck().cards, seed)

        # Print metadata
        self.game_log += "\nNew round started.\n\n"
        # Set positions.
        position_names = TexasHoldEm.POSITIONS_PER_PLAYERCOUNT[len(self.players)]
        # Post blinds.
        sb = 0
        bb = 0
        sb_name = ''
        bb_name = ''
        bb_index = -1
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
                player.amount_in = 0
        self.game_log += f"{sb_name} posts small blind (${sb}).\n"
        self.game_log += f"{bb_name} posts big blind (${bb}).\n\n"
        # Add chips here
        self.pot += sb
        self.pot += bb
        # Distribute hole cards.
        for index, player in enumerate(self.players):
            self.deck, player.hole_cards = Deck.pop(self.deck, 2)
            self.game_log += f"Dealt two cards to {player.name} in {player.position} (${player.chips}).\n"

        remaining_players = []

        # PREFLOP

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("PREFLOP", self.BIG_BLIND, self.game_log, self.players[bb_index], self.players, self.pot)

        self.game_log, remaining_players, self.pot, self.deck, flop_cards = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 3)

        # FLOP

        first = TexasHoldEm.find_first_to_act_postflop(self.players, remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("FLOP", self.BIG_BLIND, self.game_log, first, remaining_players, self.pot, community_new=flop_cards)

        self.game_log, remaining_players, self.pot, self.deck, turn_card = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 1)

        # TURN

        first = TexasHoldEm.find_first_to_act_postflop(self.players, remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("TURN", self.BIG_BLIND, self.game_log, first, remaining_players, self.pot, community_new=turn_card)

        self.game_log, remaining_players, self.pot, self.deck, river_card = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck, 1)

        # RIVER

        first = TexasHoldEm.find_first_to_act_postflop(self.players, remaining_players)

        self.game_log, remaining_players, self.pot = \
            TexasHoldEm.request_actions("TURN", self.BIG_BLIND, self.game_log, first, remaining_players, self.pot, community_new=turn_card)
        
        # TODO: "end action" and evaluate winner.
        self.game_log, remaining_players, self.pot, self.deck, river_card = \
            TexasHoldEm.end_street(self.game_log, remaining_players, self.pot, self.deck)


        if(len(remaining_players) == 1):
            game_log += f"{remaining_players[0]} collects ${self.pot} from the pot.\n"
            player.chips += self.pot
            return

        self.game_log += f"\n"
        for player in remaining_players:
            self.game_log += f"{player.name} (${player.chips}) remains.\n"
        self.deck, flop_cards = Deck.pop(self.deck, 3)

        


# Nice seed with overcards and two pocket pairs:
# 1771810701714

t = TexasHoldEm()
t.add_player("Ben", TexasHoldEm.MAX_BUY_IN)
t.add_player("Carol", TexasHoldEm.MAX_BUY_IN)
t.add_player("John", TexasHoldEm.MAX_BUY_IN)
t.add_player("Stacy", TexasHoldEm.MAX_BUY_IN)
t.add_player("Matt", TexasHoldEm.MAX_BUY_IN)
t.add_player("Jenna", TexasHoldEm.MAX_BUY_IN)
t.start_round(1771810701714)


