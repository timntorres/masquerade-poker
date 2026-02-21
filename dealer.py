from deck import Deck, Hand

class Player:
    def __init__(self, name, buy_in):
        self.name = name
        self.chips = buy_in
        self.hole_cards = []
        self.is_active = True
        self.position = ""

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

    def add_player(self, name, buy_in):
        if len(self.players) >= 6:
            return None
        new_player = Player(name, buy_in)
        self.players.append(new_player)
        print(f"{name} has bought in for ${buy_in}.")
    
    def start_round(self):

        self.deck = Deck.shuffle(Deck().cards)

        # Print metadata
        print("New round started.")
        # Set positions.
        position_names = TexasHoldEm.POSITIONS_PER_PLAYERCOUNT[len(self.players)]
        # Distribute cards.
        for index, player in enumerate(self.players):
            self.deck, player.hole_cards = Deck.pop(self.deck, 2)
            player.position = position_names[index - self.player_index_of_button]
            print(f"Dealt {player.hole_cards} to {player.name} in {player.position} (${player.chips})")


t = TexasHoldEm()
t.add_player("bb", TexasHoldEm.MAX_BUY_IN)
t.add_player("cc", TexasHoldEm.MAX_BUY_IN)
t.add_player("dd", TexasHoldEm.MAX_BUY_IN)
t.add_player("ee", TexasHoldEm.MAX_BUY_IN)
t.add_player("ff", TexasHoldEm.MAX_BUY_IN)
t.add_player("gg", TexasHoldEm.MAX_BUY_IN)
t.start_round()
