import random
import heapq

class Deck:
    
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    SUITS = ["c", "d", 'h', "s"]

    def __init__(self):
        self.cards = Deck.generate_deck()

    @staticmethod
    def generate_deck():
        deck = []
        for rank in Deck.RANKS:
            for suit in Deck.SUITS:
                deck.append(Card(f"{rank}{suit}"))
        return deck

    @staticmethod
    def shuffle(deck):
        random.shuffle(deck)
        return deck

    @staticmethod
    def pop(deck, amount=1):
        popped = deck[len(deck) - amount:]
        deck = deck[: - 1 * amount]
        return deck, popped

class Card:

    def __init__(self, card):
        self.rank = card[0]
        self.suit = card[1]
        self.value = Deck.RANKS.index(self.rank)

    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.value == other.value
    
    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.value < other.value

    @staticmethod
    def max(cards):
        max = -1
        index_of_max = -1

        for i, card in enumerate(cards):
            if(card.value > max):
                max = card.value
                index_of_max = i

        return cards[index_of_max]

    @staticmethod
    def compare(card_a, card_b):
        if(isinstance(card_a, list) and isinstance(card_b, list)):
            card_a = max(card_a)
            card_b = max(card_b)

        return card_a.value > card_b.value


class Hand:

    HANDS = [ \
                'high card', 'one pair', 'two pair', \
                'three of a kind', 'straight', 'flush', \
                'full house', 'four of a kind', 'straight flush', \
                'royal flush' \
            ]

    def __init__(self, hand_id, cards, quads, threes, pairs, kickers):
        self.hand_id = hand_id
        self.cards = cards
        self.quads = quads
        self.threes = threes
        self.pairs = pairs
        self.kickers = kickers

    @staticmethod
    def max(cards):
        return Hand.make_consecutive(cards)[-1]

    @staticmethod
    def sorted(ranks):
        return sorted(ranks, key = lambda rank: Deck.RANKS.index(rank))

    @staticmethod
    def make_consecutive(cards):
        return sorted(cards, key = lambda card: Deck.RANKS.index(card.rank))

    # Accepts five and only five cards
    @staticmethod
    def is_straight(cards):
        if(len(cards) > 5):
            print("Warning. Use has_straight when checking for straights within more than five cards.")
            return False
        elif(len(cards) < 5):
            return False

        joined = "".join(Deck.RANKS)
        ordered = "".join(str(card.rank) for card in Hand.make_consecutive(cards))
        return (ordered in joined) or (ordered == "2345A") # The wheel edge case

    @staticmethod
    def get_highest_straight_index(cards):
        if (len(cards) < 5):
            return 0 if Hand.is_straight(cards) else -1

        ordered = Hand.make_consecutive(cards)

        index_of_highest_straight = -1
        for i in range(len(cards) - 4):
            if(Hand.is_straight(cards[i:5+i])):
                index_of_highest_straight = i
        return index_of_highest_straight

    @staticmethod
    def get_max_same_suit(cards):
        suit_count = {}
        cards_of_that_suit = {}

        for card in cards:
            suit = card.suit
            if suit in suit_count:
                suit_count[suit] += 1
                cards_of_that_suit[suit] = cards_of_that_suit[suit] + [card]
            else:
                suit_count[suit] = 1
                cards_of_that_suit[suit] = [card]

        max_key = max(suit_count, key=suit_count.get)
        return cards_of_that_suit[max_key]

    @staticmethod
    def count(cards):
        card_count = {}
        for card in cards:
            if card in card_count:
                card_count[card] += 1
            else:
                card_count[card] = 1
        return card_count

    def max_rank(ranks, n=1):
        if(n == 1):
            return max(ranks, key = lambda rank: Deck.RANKS.index(rank))
        return heapq.nlargest(n, ranks, key = lambda rank: Deck.RANKS.index(rank))



    @staticmethod
    def max(cards, n=1):
        if len(cards) == 0:
            return cards

        if len(cards) == 1:
            return cards[0]

        if(n == 1):
            return max(cards, key = lambda card: Deck.RANKS.index(card.rank))

        return heapq.nlargest(n, cards, key = lambda card: Deck.RANKS.index(card.rank))


    # It's gonna be sets of seven cards needing classification; 
    # the five community cards and the two hole cards.
    # Return the five effective cards (i.e. what constitutes the hand) as well as the hand name.
    @staticmethod
    def classify(cards):
        ordered = Hand.make_consecutive(cards)
        suitless = [card.rank for card in ordered]

        count = Hand.count(suitless)

        quadded_ranks = [key for key, value in count.items() if value == 4] 
        threed_ranks = [key for key, value in count.items() if value == 3]
        paired_ranks = [key for key, value in count.items() if value == 2]
        # Since "three pair" isn't a hand, only the top two pairs matter; 
        # the third pair's rank could serve as a kicker, though.
        """
            BOARD: KKQT3
            Person A:  Q T
            Person B:  Q 3
        """
        paired_ranks = Hand.max_rank(paired_ranks, 2)

        quads = {}
        threes = {}
        pairs = {}
        kicker_candidates = []
        hand_id = ''
        final_hand = []
        kickers = []

        for card in ordered:
            if(card.rank in quadded_ranks):
                quads.setdefault(card.rank, []).append(card)
            elif (card.rank in threed_ranks):
                threes.setdefault(card.rank, []).append(card)
            elif (card.rank in paired_ranks):
                pairs.setdefault(card.rank, []).append(card)
            else:
                kicker_candidates.append(card)

        # Detect flush
        is_flush = False
        max_same_suit = Hand.get_max_same_suit(ordered)
        if(len(max_same_suit) >= 5):
            is_flush = True

        # Detect any straight
        pruned = ordered
        straight_index = Hand.get_highest_straight_index(cards)
        has_straight = False
        if(straight_index != -1):
            pruned = cards[straight_index:straight_index + 5]
            has_straight = True

        # Classify
        max_straight_flush_index = Hand.get_highest_straight_index(max_same_suit)

        if(is_flush and max_straight_flush_index != -1):
            if(''.join([card.rank for card in max_same_suit[max_straight_flush_index:]]) == 'TJQKA'):
                hand_id = 'royal flush'
            hand_id = 'straight flush'
            final_hand = max_same_suit[max_straight_flush_index:max_straight_flush_index + 5]
        elif len(quadded_ranks) != 0:
            hand_id = 'four of a kind'
            # This line technically could fail in cases of quads over quads within the same hand,
            # but with two hole cards and five community cards, quads over quads will never
            # occur.

            # Should avoid kicker_candidates because, of course, ranks of three-of-a-kind and paired cards
            # can serve as kickers in cases of quads.
            kickers.append(Hand.max([card for card in ordered if card.rank not in quadded_ranks]))
            final_hand = list(quads.values())[-1] + kickers
        elif (len(threed_ranks) == 1 and len(paired_ranks)  >= 1) \
            or (len(threed_ranks) > 1):
            hand_id = 'full house'
            # Find and add the max three
            max_threed_rank = Hand.max_rank(threed_ranks)
            final_hand = threes[max_threed_rank]
            # Join the pairs and the remaining threes
            remaining = []
            for rank in threes.keys():
                if rank == max_threed_rank:
                    continue
                remaining += threes[rank]
            for rank in pairs.keys():
                remaining += pairs[rank]
            # Order them
            remaining = Hand.make_consecutive(remaining)
            # Stick the last two onto the end
            final_hand += remaining[-2:]

            # Hardcode the effective three and the effective pair
            threes = {max_threed_rank: threes[max_threed_rank]}
            pairs = {remaining[-1].rank: remaining[-2:]}

        elif is_flush:
            hand_id = 'flush'
            max_same_suit = Hand.make_consecutive(max_same_suit)
            start_index = max(len(max_same_suit) - 5, 0)
            final_hand = max_same_suit[start_index:start_index + 5]
        elif has_straight:
            hand_id = 'straight'
            final_hand = pruned
        elif len(threed_ranks) == 1:
            hand_id = 'three of a kind'
            kickers = Hand.max(kicker_candidates, 2)
            final_hand = list(threes.values())[-1] + kickers
        elif len(paired_ranks) == 2:
            hand_id = 'two pair'
            kickers.append(Hand.max([card for card in ordered if card.rank not in quadded_ranks]))
            final_hand = list(pairs.values())[-1] + list(pairs.values())[-2] + kickers
        elif len(paired_ranks) == 1:
            hand_id = 'one pair'
            kickers = Hand.max(kicker_candidates, 3)
            final_hand = list(pairs.values())[-1] + kickers
        else:
            hand_id = 'high card'
            kickers = Hand.max(kicker_candidates, 5)
            final_hand = kickers


        return Hand(hand_id, cards, quads, threes, pairs, kickers)

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
t.add_player("gg", TexasHoldEm.MAX_BUY_IN)
t.start_round()
