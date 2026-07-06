import json
from deck import Deck, Hand, Card
from itertools import combinations
import random



def estimate_straight_combos(community_cards):
    deck_ = set(Deck.generate_deck())
    remaining = set.difference(deck_, community_cards)
    straight_count = 0
    for hole_cards in combinations(remaining, 2):
        unordered = list(community_cards) + list(hole_cards)

        straight_hand = -1

        straight_hand = \
            Hand.get_highest_straight_index( \
                Hand.make_consecutive(unordered)
            )

        if(straight_hand == -1):
            continue
        straight_count += 1
    return straight_count


def estimate_flops():
    straight_cache = {}

    deck_ = set(Deck.generate_deck())
    # For each river, count the number of hole cards that create a straight
    # that beat the board.
    straight_counts = {}
    board_count = 0
    straight_cache = {}
    for community_cards in combinations(deck_, 3):

        remaining = set.difference(deck_, community_cards)
        straight_count = 0

        for hole_cards in combinations(remaining, 2):
            unordered = community_cards + hole_cards
            hand_set = frozenset([card.rank for card in unordered])

            straight_hand = -1

            if hand_set in straight_cache:
                straight_hand = straight_cache[hand_set]
            else:
                straight_hand = \
                    Hand.get_highest_straight_index( \
                        Hand.make_consecutive(unordered)
                    )
                straight_cache[hand_set] = straight_hand

            if(straight_hand == -1):
                continue
            straight_count += 1

        straight_counts[straight_count] = \
            straight_counts.setdefault(straight_count, 0) + 1

        board_count += 1
        if(board_count % 5000 == 0):
            print(f"Cache size: {len(straight_cache)}")
            print(f"{board_count} / 22100\n({board_count/22100*100}%)\n\n")
            print(straight_counts)
            with open("straight_rough_count_flop.json", "w") as file:
                json.dump(straight_counts, file, indent=4)


def estimate_turns():
    straight_cache = {}

    deck_ = set(Deck.generate_deck())
    # For each river, count the number of hole cards that create a straight
    # that beat the board.
    straight_counts = {}
    board_count = 0
    straight_cache = {}
    for community_cards in combinations(deck_, 4):

        remaining = set.difference(deck_, community_cards)
        straight_count = 0

        for hole_cards in combinations(remaining, 2):
            unordered = community_cards + hole_cards
            hand_set = frozenset([card.rank for card in unordered])

            straight_hand = -1

            if hand_set in straight_cache:
                straight_hand = straight_cache[hand_set]
            else:
                straight_hand = \
                    Hand.get_highest_straight_index( \
                        Hand.make_consecutive(unordered)
                    )
                straight_cache[hand_set] = straight_hand

            if(straight_hand == -1):
                continue
            straight_count += 1

        straight_counts[straight_count] = \
            straight_counts.setdefault(straight_count, 0) + 1

        board_count += 1
        if(board_count % 5000 == 0):
            print(f"Cache size: {len(straight_cache)}")
            print(f"{board_count} / 270725\n({board_count/270725*100}%)\n\n")
            print(straight_counts)
            with open("___straight_rough_count_turn.json", "w") as file:
                json.dump(straight_counts, file, indent=4)


def estimate_rivers():
    straight_cache = {}

    deck_ = set(Deck.generate_deck())
    # For each river, count the number of hole cards that create a straight
    # that beat the board.
    straight_counts = {}
    board_count = 0
    straight_cache = {}
    for community_cards in combinations(deck_, 5):

        remaining = set.difference(deck_, community_cards)
        board_beating_straight_count = 0

        for hole_cards in combinations(remaining, 2):
            unordered = community_cards + hole_cards
            hand_set = frozenset([card.rank for card in unordered])

            straight_hand = -1
            straight_board = -1

            if hand_set in straight_cache:
                straight_hand = straight_cache[hand_set]
            else:
                straight_hand = \
                    Hand.get_highest_straight_index( \
                        Hand.make_consecutive(unordered)
                    )
                straight_cache[hand_set] = straight_hand

            if(straight_hand == -1):
                continue

            board_set = frozenset([card.rank for card in community_cards])

            if board_set in straight_cache:
                straight_board = straight_cache[board_set]
            else:
                straight_board = \
                        Hand.get_highest_straight_index( \
                            Hand.make_consecutive(list(community_cards))
                        )
                straight_cache[board_set] = straight_board

            if(straight_hand > straight_board):
                board_beating_straight_count += 1

        straight_counts[board_beating_straight_count] = \
            straight_counts.setdefault(board_beating_straight_count, 0) + 1

        board_count += 1
        if(board_count % 5000 == 0):
            print(f"Cache size: {len(straight_cache)}")
            print(f"{board_count} / 2598960\n({board_count/2598960*100}%)\n\n")
            print(straight_counts)
            with open("___straight_rough_count_river_.json", "w") as file:
                json.dump(straight_counts, file, indent=4)

