from game_logic import build_heuristics
import random
from deck import Deck

def test_heuristics(trials = 10):

    for i in range(trials):
        print(f'\n\nTRIAL {i}/{trials}.\n\n')


        deck_ = Deck.generate_deck()
        random.shuffle(deck_)
        deck_, community_cards = Deck.pop(deck_, 3)
        deck_, hole_cards = Deck.pop(deck_, 2)
        print(f"{hole_cards}")
        print(build_heuristics(hole_cards, []))


        print(f'FLOP {community_cards}')
        print(build_heuristics(hole_cards, community_cards))

        deck_, turn_card = Deck.pop(deck_, 1)
        community_cards += turn_card
        print(f'TURN {community_cards}')
        print(build_heuristics(hole_cards, community_cards))

        deck_, river_card = Deck.pop(deck_, 1)
        community_cards += river_card
        print(f'RIVER {community_cards}')
        print(build_heuristics(hole_cards, community_cards))

test_heuristics()