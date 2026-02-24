import heapq
import math
import time
import copy
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
    def pop(deck, amount=1):
        popped = deck[len(deck) - amount:]
        deck = deck[: - 1 * amount]
        return deck, popped

class SameRank:
    def __init__(self, id, amount, rank, constituents):
        self.id = id
        self.amount = amount
        self.rank = rank
        self.constituents = constituents


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

    def min(cards):
        min = math.inf
        index_of_max = -1

        for i, card in enumerate(cards):
            if(card.value < min):
                min = card.value
                index_of_max = i

        return cards[index_of_max]


    @staticmethod
    def min_rank(ranks, n=1):
        if(n == 1):
            return min(ranks, key = lambda rank: Deck.RANKS.index(rank))
        return heapq.nsmallest(n, ranks, key = lambda rank: Deck.RANKS.index(rank))

    @staticmethod
    def max_rank(ranks, n=1):
        if(n == 1):
            return max(ranks, key = lambda rank: Deck.RANKS.index(rank))
        return heapq.nlargest(n, ranks, key = lambda rank: Deck.RANKS.index(rank))

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
    def compare_rank(rank_a, rank_b):
        if(rank_a == -1):
            return False
        elif(rank_b == -1):
            return True
        return Deck.RANKS.index(rank_a) > Deck.RANKS.index(rank_b)

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

    def __init__(self, player, hand_id, cards, quads, threes, pairs, kickers):
        self.player = player
        self.hand_id = hand_id
        self.cards = cards
        self.quads = quads
        self.threes = threes
        self.pairs = pairs
        self.kickers = kickers

    def __str__(self):
        return f"{self.player} {self.cards} {self.hand_id}\n"
    
    __repr__ = __str__


    @staticmethod
    def max(cards):
        return Hand.make_consecutive(cards)[-1]

    @staticmethod
    def sorted(ranks):
        return sorted(ranks, key = lambda rank: Deck.RANKS.index(rank))

    @staticmethod
    def make_consecutive(cards, reversed=False):
        return sorted(cards, key = lambda card: Deck.RANKS.index(card.rank), reverse=reversed)

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

    @staticmethod
    def max(cards, n=1):
        if len(cards) == 0:
            return cards

        if len(cards) == 1:
            return cards[0]

        if(n == 1):
            return max(cards, key = lambda card: Deck.RANKS.index(card.rank))

        return heapq.nlargest(n, cards, key = lambda card: Deck.RANKS.index(card.rank))

    @staticmethod
    def filter_by_highest(hands, getter):
        highest_rank = -1
        for hand in hands:
            if(Card.compare_rank(getter(hand), highest_rank)):
                highest_rank = getter(hand)
        return [hand for hand in hands if getter(hand) == highest_rank]

    # For things like kickers, where
    # AKQ522
    # AKQ622
    # The first three highest cards are tied, and the kicker is down the line.
    @staticmethod
    def compare_sequence(hands, getter):
        candidates = copy.deepcopy(hands)

        if(len(candidates) < 2):
            return candidates
        sequence_length = len(getter(candidates[0]))

        # Sanity check
        for hand in candidates:
            if(len(getter(hand)) != sequence_length):
                print("Warning. Same hands have sequences of different lengths.")
                print(f"{getter(candidates[0])} vs {getter(hand)}")
                exit()
        
        index = 0
        while (len(candidates) > 1) and (index <= sequence_length - 1):
            candidates = Hand.filter_by_highest(candidates, lambda h: getter(h)[index].rank)
            index += 1

        return candidates



    @staticmethod
    def compare_kickers(hands):
        if(len(hands) < 2):
            return hands[0]
        kicker_length = len(hands[0].kickers)

        # Sanity check
        for hand in hands:
            if(len(hand.kickers) != kicker_length):
                print("Warning. Same hands have kickers of different lengths.")
                print(f"{hands[0].kickers} vs {hand.kickers}")
                exit()
        
        candidates = copy.deepcopy(hands)
        
        while (len(candidates) > 1) and (kicker_length > 0):
            candidates = Hand.filter_by_highest(candidates, lambda h: h.kickers[0].rank)
        return candidates

    @staticmethod
    def find_winners(players, community_cards):
        hands = {}
        
        for player in players:
            hand = Hand.classify(player.hole_cards + community_cards, player)

            hands.setdefault(hand.hand_id, []).append(hand)
        
        max_value_hand = max(hands.keys(), key = lambda hand: Hand.HANDS.index(hand))

        winning_hands = hands[max_value_hand]
        
        # One winner
        if(len(winning_hands) == 1):
            return winning_hands
    
        # Tiebreakers

        # Royal flush over royal flush is always a chop.
        if(max_value_hand == 'royal flush'):
            return winning_hands
        # Hands where the highest card wins
        elif max_value_hand == 'flush' or \
             max_value_hand == 'high card':
            tie_breaker_winners = Hand.compare_sequence(winning_hands, lambda h: h.cards)
            return tie_breaker_winners
        
        # Hands with the wheel edge case (Highest low card wins, compare ace existing when 2 found)
        elif max_value_hand == 'straight flush' or \
             max_value_hand == 'straight':
            lowest_card = {}
            for hand in winning_hands:
                lowest_card.setdefault(Card.min(hand.cards).rank, []).append(hand)
            highest_low_card = Card.max_rank(list(lowest_card.keys()))

            # Wheel edge case
            if(highest_low_card == 2):
                beats_wheels = []
                for hand in lowest_card[2]:
                    ranks = [card.rank for card in hand.cards]
                    if 'A' in ranks:
                        continue
                    beats_wheels.append(hand)
                if(len(beats_wheels) != 0):
                    return beats_wheels
            
            return lowest_card[highest_low_card]
        
        elif max_value_hand == 'four of a kind':
            # Compare the quad
            highest_quads = Hand.filter_by_highest(winning_hands, lambda h: h.quads.rank)
            # Compare the kicker
            highest_kicker = Hand.compare_sequence(highest_quads, lambda h: h.kickers)
            return highest_kicker
        elif max_value_hand == 'full house':
            # Compare the three-of-a-kind
            highest_three = Hand.filter_by_highest(winning_hands, lambda h: h.threes.rank)
            # Compare the pair
            highest_pair = Hand.filter_by_highest(highest_three, lambda h: Card.max_rank(list(h.pairs.keys())))
            return highest_pair    
        elif max_value_hand == 'three of a kind':
            # Compare the three
            highest_three = Hand.filter_by_highest(winning_hands, lambda h: h.threes.rank)
            # Compare the kickers
            highest_kicker = Hand.compare_sequence(highest_three, lambda h: h.kickers)
            return highest_kicker
        elif max_value_hand == 'two pair':
            # Compare the top pair:
            highest_pair = Hand.filter_by_highest(winning_hands, lambda h: Card.max_rank(list(h.pairs.keys())))
            # Compare the bottom pair:
            highest_bottom_pair = Hand.filter_by_highest(highest_pair, lambda h: Card.min_rank(list(h.pairs.keys())))
            # Compare the kicker:
            highest_kicker = Hand.compare_sequence(highest_bottom_pair, lambda h: h.kickers)
            return highest_kicker
        elif max_value_hand == 'one pair':
            # Compare the pair:
            highest_pair = Hand.filter_by_highest(winning_hands, lambda h: h.pairs[0][0].rank)
            # Compare the kickers:
            highest_kicker = Hand.compare_sequence(highest_pair, lambda h: h.kickers)
            return highest_kicker


    @staticmethod
    def flatten_pairs(pairs):
        list_of_lists = list(pair.constituents for pair in pairs.values())
        flattened_cards = [card for pair in list_of_lists for card in pair]
        return flattened_cards

    # It's gonna be sets of seven cards needing classification; 
    # the five community cards and the two hole cards.
    # Return the five effective cards (i.e. what constitutes the hand) as well as the hand name.
    @staticmethod
    def classify(cards, player=None):
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
        paired_ranks = Card.max_rank(paired_ranks, 2)

        quads = None
        threes = None
        pairs = None
        max_pair_rank = -1

    # Quads: will always have 1
        if(len(quadded_ranks) == 1):
            quads = SameRank('quads', 4, quadded_ranks[0], [])
        elif(len(quadded_ranks) > 1):
            print(f"WARNING. {quadded_ranks} detected an impossible number of quads in {ordered}.")
            exit()
    # Threes: will have 1 or 2
        if(len(threed_ranks) == 1):
            max_three = max(threed_ranks)
            threes = SameRank('threes', 3, max_three, [])
        elif(len(threed_ranks) == 2):
            # Treat the lower one as a pair
            paired_ranks.append(min(threed_ranks))
        elif(len(threed_ranks) > 2):
            print(f"WARNING. {threed_ranks} detected an impossible number of threes in {ordered}.")
            exit()
    # Pairs: could have 1, 2, or 3
        if(len(paired_ranks) > 0):
            pairs = {}
            # Prune to the highest 2
            paired_ranks = Card.max_rank(paired_ranks, 2)
            for pair in paired_ranks:
                pairs[pair] = SameRank('pairs', 2, pair, [])

            max_pair_rank = Card.max_rank(list(pairs.keys()))

        kicker_candidates = []
        hand_id = ''
        final_hand = []
        kickers = []

        for card in ordered:
            if(quads is not None and card.rank == quads.rank):
                quads.constituents.append(card)
            elif (threes is not None and card.rank == threes.rank):
                threes.constituents.append(card)
            elif pairs is not None and card.rank in pairs:
                pairs[card.rank].constituents.append(card)
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
        elif quads is not None:
            hand_id = 'four of a kind'
            kickers.append(Hand.max([card for card in ordered if card.rank != quads.rank]))
            final_hand = quads.constituents + kickers
        elif ((threes is not None) and (pairs is not None)):
            hand_id = 'full house'
            final_hand = threes.constituents + pairs[max_pair_rank].constituents
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
            final_hand = threes.constituents + kickers
        elif len(paired_ranks) == 2:
            hand_id = 'two pair'
            kickers.append(Hand.max(kicker_candidates))
            
            flattened_cards = Hand.flatten_pairs(pairs)

            final_hand = flattened_cards + kickers

        elif len(paired_ranks) == 1:
            hand_id = 'one pair'
            kickers = Hand.max(kicker_candidates, 3)

            values = [*list(pairs.values())]
            pairs = [item.constituents for item in values]

            flattened_cards = [card for pair in pairs for card in pair]
            final_hand = flattened_cards + kickers
        else:
            hand_id = 'high card'
            kickers = Hand.max(kicker_candidates, 5)
            final_hand = kickers


        return Hand(player, hand_id, final_hand, quads, threes, pairs, kickers)
    