import random

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

    HANDS = \
    { 
        "royal flush": 
            {
                "value": 9, "kickers": 0
            },
        "straight flush": 
            {
                "value": 8, "kickers": 0
            },
        "four of a kind": 
            {
                "value": 7, "kickers": 1
            },
        "full house": 
            {
                "value": 6, "kickers": 0
            },
        "flush": 
            {
                "value": 5, "kickers": 0
            },
        "straight": 
            {
                "value": 4, "kickers": 0
            },
        "three of a kind": 
            {
                "value": 3, "kickers": 2
            },
        "two pair": 
            {
                "value": 2, "kickers": 1
            },
        "one pair": 
            {
                "value": 1, "kickers": 4
            },
        "high card": 
            {
                "value": 0, "kickers": 4
            }
    }

    @staticmethod
    def max(cards):
        return Hand.make_consecutive(cards)[-1]

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


    # It's gonna be sets of seven cards needing classification; 
    # the five community cards and the two hole cards.
    @staticmethod
    def classify(cards):
        ordered = Hand.make_consecutive(cards)
        suitless = [card.rank for card in ordered]
        count = Hand.count(suitless)
        setted = set(count.keys())
        ordered_without_duplicates = sorted(list(setted), key = lambda rank: Deck.RANKS.index(rank))

        # Flush logic
        is_flush = False
        max_same_suit = Hand.get_max_same_suit(ordered)
        if(len(max_same_suit) >= 5):
            is_flush = True

        
            

        # Any straight logic
        pruned = ordered
        straight_index = Hand.get_highest_straight_index(cards)
        has_straight = False
        if(straight_index != -1):
            pruned = cards[straight_index:straight_index + 5]
            has_straight = True
                    

        num_pairs = sum([1 for num in count.values() if num == 2])

        # print(f"cards: {cards}\nordered: {ordered}\nsuitless: {suitless}\ncount: {count}\nsetted: {setted}\nordered without duplicates: {ordered_without_duplicates}")
        
        # Straight flush?
        if(is_flush and Hand.get_highest_straight_index(max_same_suit) != -1):
            # Royal flush?
            if(max(max_same_suit).rank == 'A' and min(max_same_suit).rank == 'T'):
                return 'royal flush'
            return 'straight flush'
        # Four of a kind?
        elif max(count.values()) == 4:
            return 'four of a kind'
        # Full house?
        elif 3 in count.values() and 2 in count.values():
            return 'full house'
        # Flush?
        elif is_flush:
            return 'flush'
        # Straight?
        elif has_straight:
            return 'straight'
        # Three of a kind?
        elif 3 in count.values():
            return 'three of a kind'
        # Two pair?
        elif num_pairs >= 2:
            return 'two pair'
        # One pair?
        elif(num_pairs == 1):
            return 'one pair'
        
        return 'high card'

deck = Deck.shuffle(Deck().cards)
deck, cards = Deck.pop(deck, 7)

# cards = Card("Ad"), Card("2d"), Card("3d"), Card("4d"), Card("5d")
cards = Card("Ad"), Card("Ah"), Card("Td"), Card("Kd"), Card("Qd"), Card("Jd")
# cards = Card("Ad"), Card("Th"), Card("Td"), Card("Kd"), Card("Qd"), Card("Jd")

print(f"CARDS: {cards}\nRESULT: {Hand.classify(cards)}")
