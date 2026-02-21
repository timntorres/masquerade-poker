from dealer import Deck, Hand

HAND_PROBABILITIES = \
{ 
    "royal flush": 0.00000154,
    "straight flush": 0.0000139,
    "four of a kind": 0.0002401,
    "full house": 0.001441,
    "flush": 0.001965,
    "straight": 0.003925,
    "three of a kind": 0.021128,
    "two pair": 0.047539,
    "one pair": 0.422569,
    "high card": 0.501177
}
# Sanity check
print(f"Should be 1: {sum(HAND_PROBABILITIES.values())}")

trials = 10000
results = {}
for i in range(trials):
    deck = Deck.shuffle(Deck().cards)
    deck, cards = Deck.pop(deck, 5)

    hand_object = Hand.classify(cards)

    result = hand_object.hand_id 

    if result in results:
        results[result] += 1
    else:
        results[result] = 1
print(results)

# PERCENT ERROR:
for hand in HAND_PROBABILITIES.keys():
    actual = 0
    percent_error = "undefined"
    if(hand in results.keys()):
        actual = results[hand]
        percent_error = (HAND_PROBABILITIES[hand] * trials - actual)/actual
        # print(f"Hand: {hand}\n  expected: {HAND_PROBABILITIES[hand] * trials}\n  actual: {actual}")
    print(f"{hand}: {percent_error}")
