

class Hand:
    CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    @staticmethod
    def strip_suits(cards):
        return [card[0] for card in cards]

    @staticmethod
    def max(cards):

        suitless = Hand.strip_suits(cards)
        max = -1
        index_of_max = -1

        for i, card in enumerate(suitless):
            if(Hand.CARDS.index(card) > max):
                max = Hand.CARDS.index(card)
                index_of_max = i

        return cards[index_of_max]

    @staticmethod
    def compare(card_a, card_b):

        if(isinstance(card_a, list) and isinstance(card_b, list)):
            card_a = max(card_a)
            card_b = max(card_b)

        return Hand.CARDS.index(card_a[0]) > Hand.CARDS.index(card_b[0])
        

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
    def classify(cards):
        suitless = Hand.strip_suits(cards)
        # Royal flush?
        if(set(suitless) == {'A', 'K', 'Q', 'J', 'T'}):
            return 

