class Card:
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    SUITS = ["c", "d", 'h', "s"]

    def __init__(self, card):
        self.rank = card[0]
        self.suit = card[1]
        self.value = Card.RANKS.index(self.rank)

    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    __repr__ = __str__

    @staticmethod
    def generate_deck():
        deck = {}
        for rank in Card.RANKS:
            for suit in Card.SUITS:
                deck[f"{rank}{suit}"] = Card(rank, suit)
        return deck

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
    def make_consecutive(cards):
        return sorted(cards, key = lambda card: Card.RANKS.index(card.rank))

    @staticmethod
    def is_straight(cards):
        joined = Card.RANKS[-1:].join()
        ordered = Hand.make_consecutive(cards).join()
        return ordered in joined

    @staticmethod
    def is_flush(cards):
        suits = ()

        for card in cards:
            suits.add(card.suit)
        
        return len(suits) == 1

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
        print(f"cards: {cards}\nordered: {ordered}\nsuitless: {suitless}\ncount: {count}\nsetted: {setted}")
        """
        # Royal flush?
        if(set(suitless) == {'A', 'K', 'Q', 'J', 'T'}):
            return 'royal flush'
        # Straight flush?
        elif(Hand.is_straight(cards) and Hand.is_flush(cards))
            return 'straight flush'
        # Four of a kind?
        """

s = [Card("Ad"), Card("2d"), Card("5h"), Card("7d"), Card("2s"), Card("Tc")]
print(Card("Ad"))
Hand.classify(s)