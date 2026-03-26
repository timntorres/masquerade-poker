import datetime
import copy

class Phases:
    GAME_START = "game start"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    GAME_END = "game end"

class Actions:

    SHUFFLE = 'shuffle'
    CHECK = 'check'
    CALL = 'call'
    BET = 'bet'
    RAISE = 'raise'
    FOLD = 'fold'
    SAY = 'say'
    THINK = 'think'
    WIN = 'win'

    PREP_PHRASES = {
        SHUFFLE: 'with',
        CHECK: '',
        CALL: '',
        BET: '',
        RAISE: 'to',
        FOLD: '',
        SAY: '',
        THINK: '',
        WIN: ''
    }

class Action:


    def __init__(self, phase, subject, action, object=None):
        self.subject = subject
        self.action = action
        self.object = object

        self.time = datetime.now()
        self.phase = phase

    def __str__(self):

        preposition = Actions.PREP_PHRASES[self.action]
        preposition = " " + preposition if preposition != "" else ""
        object =  " " + self.object if self.object != "" else ""

        formatted = f"{self.name} {self.action}s{preposition}{object}."

        print(self.action + " versus " + Actions.IS)
        if(self.action == Actions.IS):
            formatted = f"{object} {self.action} {self.name}."

        return "HELLO!?!?!?!?!!?!??!"

    __repr__ = __str__

class Pot:

    # "parent pot" is "side pot" in poker terms.
    def __init__(self, players, amount, parent_pot=None):
        self.player_set = set(players)

        # Chips while action is taking place.
        self.player_bets = {}
        for player in self.player_set:
            self.player_bets[player] = 0

        self.amount = amount
        self.parent_pot = parent_pot

    # This doesn't do any of the subtraction from stacks.
    def receive_bet(pot, player, amount):
        # Make sure player exists in pot
        if(player not in pot.player_bets.keys):
            print(f"Warning. Player {player} not in player_bets.")
            return pot, player

        pot.player_bets[player] = amount
        return pot, player

    def end_street(self):
        # Accumulate chips in center
        # Zero out bets
        for player in self.player_bets.keys():
            self.amount += self.player_bets[player]
            self.player_bets[player] = 0

    # Call this when a particular player folds.
    # Return the side pot excluding that player.
    def create_side_pot(self, player, surplus):
        new_player_set = copy.copy(self.player_set)
        new_player_set.discard(player)
        return Pot(new_player_set, surplus, self)



    # For when a particular player goes all-in.
    # This current pot will beocme the child of the returned pot.
    def create_child(self, player):
        child = Pot(self.player_set.discard(player), 0, )



class Snapshot:
    # A copy of the entire game's state when a given action takes place.
    def __init__(self):
        return


# Keeps the state of the entire Hold-Em game.
class Round:

    VERBOSE = True

    def __init__(self, id, players):
        self.id = id
        self.time = datetime.now()
        self.players = []
        self.actions = []
        self.last = False
        self.pot = None

        self.button_index = 0


    def log_action(self, phase, subject, action, object=None):
        self.actions.append(Action(phase, subject, action, object=None))

        if(Round.VERBOSE):
            print(self.actions[-1])


    def get_log_string(self):
        log_string = f"Round #{self.id} – {self.time}"
        phase = ""
        for action in self.actions:
            if(action.phase != phase):
                log_string != f"\n\n{action.phase.upper()}\n\n"
                phase = action.phase
            log_string += action
            log_string += "\n"
        return log_string

    def initialize_pot(self):
        self.pot = Pot(self.players, 0, parent_pot=None)

    def assign_positions(self):
        #TODO: This was copy pasted from Dealer, set this up and make it play nice
        # player being weirdly scoped makes it a little weird
        # 1. What logic should be transferred to unity?
        # 2. Ideally, there's like a distilled version of the object that exists here
        # How do you link objects togehter?

        # I do think there's something elegant about the separation of functions and states

        self.button_index += 1
        self.button_index %= len(self.players)

        for player in self.players:
            player.init_round()

        if(len(self.players) <= 1): 
            print(f"{len(self.players)} player(s) isn't enough to play poker.")
            return game_log

        self.game_log = game_log
    
        self.deck = shuffle(Deck.generate_deck())

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
