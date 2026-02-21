from deck import Deck, Hand
from ollama import chat
import string

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

    def build_local_context(self, is_check, min_raise):
        check_or_call = "call"
        if(is_check):
            check_or_call = "check"

        return f"""\nYour name is {self.name}. \
You are an expert at No-Limit Hold 'Em who makes extremely accurate decisions incredibly quickly. \
It's your {self.hand_number}th hand at this table. \
You have {self.chips} in chips. \
You've been dealt {self.hole_cards}. \
It's your turn to act. \n
Respond with exactly one word: "call," "fold," or "raise." If you decide to "raise," include exactly one number between {min_raise} and {self.chips} to represent the amount by which you'd like to raise."""

    def act(self, community_context, prev_highest_bet, min_raise):
        is_check = self.amount_in == prev_highest_bet

        total_context = community_context + self.build_local_context(is_check, min_raise)

        print(total_context)

        response = chat(model='glm-4.7-flash', messages=[
        {
            'role': 'user',
            'content': total_context,
        },
        ])

        print(response.message.content)
        processed = response.message.content.strip().lower().maketrans('', '', string.punctuation)
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
        prev_highest_bet = 0
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
        prev_highest_bet = bb
        min_raise = bb
        # Distribute cards.
        for index, player in enumerate(self.players):
            self.deck, player.hole_cards = Deck.pop(self.deck, 2)
            self.game_log += f"Dealt two cards to {player.name} in {player.position} (${player.chips}).\n"

        self.game_log += "\nPREFLOP:\n"
        # Bet, call, or fold.
        # First to act is to the left of big blind.
        action_ends = False

        i = (bb_index + 1)%len(self.players)
        last_to_act = self.players[bb_index]
        inactive = set()
        prev_actor = None
        while not action_ends:

            player = self.players[i]

            if player in inactive:
                i += 1
                i %= len(self.players)
                continue

            action, bet_size = player.act(self.game_log, prev_highest_bet, min_raise)

            self.game_log += f"{player.name} {action}s"
            if action == "raise":
                self.game_log += f" to ${player.amount_in}"
                min_raise = player.amount_in - prev_highest_bet
                prev_highest_bet = player.amount_in
                last_to_act = prev_actor

            if player.all_in:
                self.game_log += f" and is all-in"
            self.game_log += ".\n"
            
            if action == "fold" or player.all_in:
                inactive.add(player)
            else:
                prev_actor = player

            everyone_folded = (len(inactive) == len(self.players) - 1)
            pot_is_right = (player == last_to_act and action != "raise")
            if(everyone_folded or pot_is_right):
                print(f"Everyone folded? {everyone_folded}. Pot's right? {pot_is_right}.")
                action_ends = True

            i += 1
            i %= len(self.players)


t = TexasHoldEm()
t.add_player("Ben", TexasHoldEm.MAX_BUY_IN)
t.add_player("Carol", TexasHoldEm.MAX_BUY_IN)
t.add_player("John", TexasHoldEm.MAX_BUY_IN)
t.add_player("Stacy", TexasHoldEm.MAX_BUY_IN)
t.add_player("Matt", TexasHoldEm.MAX_BUY_IN)
t.add_player("Jenna", TexasHoldEm.MAX_BUY_IN)
t.start_round(seed=0)


