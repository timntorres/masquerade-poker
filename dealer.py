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

    def build_local_context(self):
        return f"""
            It's your {self.hand_number}th hand at this table. \
            You have {self.chips} in chips. \
            You've been dealt {self.hole_Cards}.
        """

    def act(self, community_context):
        total_context = self.build_local_context() + community_context

        print(total_context)

        response = chat(model='gemma3', messages=[
        {
            'role': 'Poker Expert',
            'content': f'{total_context}',
        },
        ])
        print(response.message.content)

    def post_blind(self, amount):
        effective_blind = min(amount, self.chips)
        self.chips -= effective_blind
        if(self.chips == 0):
            self.all_in = True
        return effective_blind
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
        self.deck = Deck.shuffle(Deck().cards)
        self.players = []
        self.player_index_of_button = 0
        self.game_log = ''

    def add_player(self, name, buy_in):
        if len(self.players) >= 6:
            return None
        new_player = Player(name, buy_in)
        self.players.append(new_player)
        self.game_log += f"{name} buys in for ${buy_in}.\n"
    
    def start_round(self):

        self.deck = Deck.shuffle(Deck().cards)

        # Print metadata
        self.game_log += "\n\nNew round started.\n\n"
        # Set positions.
        position_names = TexasHoldEm.POSITIONS_PER_PLAYERCOUNT[len(self.players)]
        # Post blinds.
        sb = 0
        bb = 0
        sb_name = ''
        bb_name = ''
        for index, player in enumerate(self.players):
            player.position = position_names[index - self.player_index_of_button]
            if (player.position == "SB") or (len(self.players) == 2 and player.position == "BTN"):
                sb = player.post_blind(TexasHoldEm.SMALL_BLIND)
                sb_name = player.name
            elif (player.position == "BB"):
                bb = player.post_blind(TexasHoldEm.BIG_BLIND)
                bb_name = player.name
        self.game_log += f"{sb_name} posts small blind (${sb}).\n"
        self.game_log += f"{sb_name} posts big blind (${bb}).\n"
        # Add chips here
        self.pot += sb
        self.pot += bb
        # Distribute cards.
        for index, player in enumerate(self.players):
            self.deck, player.hole_cards = Deck.pop(self.deck, 2)
            self.game_log += f"Dealt two cards to {player.name} in {player.position} (${player.chips}).\n"

        print(self.game_log)

t = TexasHoldEm()
t.add_player("bb", TexasHoldEm.MAX_BUY_IN)
t.add_player("cc", TexasHoldEm.MAX_BUY_IN)
t.add_player("dd", TexasHoldEm.MAX_BUY_IN)
t.add_player("ee", TexasHoldEm.MAX_BUY_IN)
t.add_player("ff", TexasHoldEm.MAX_BUY_IN)
t.add_player("gg", TexasHoldEm.MAX_BUY_IN)
t.start_round()


