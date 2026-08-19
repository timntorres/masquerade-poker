from game_structs import HoldemRound, Action, Player, Snapshot, T, Pot, PotQueue
from constants import Phases, Actions, Positions, Subjects
from deck import Deck, Hand, Card
from utils import init_rand, shuffle, get_time, get_nanoseconds, update
from game_save import save_game, generate_speech
from heuristics_preprocessor import estimate_straight_combos

import anthropic
import json

import random
import math
round_ = round # fml for naming the HoldemRound instance round
import time
import copy

GUIDELINES="""
# General Strategy Guidelines for No-Limit Hold'Em

## How to decide

Work through these in order. Each step narrows your options; don't skip ahead.

**1. What does the pot math require?**
If facing a bet, compare the size of the call to the size of the pot after you
call. That ratio is the minimum chance your hand needs to be best (or to
improve to best) for calling to break even. You don't need to be exact — just
don't call a bet that's bigger than the pot with a hand that's rarely best.

**2. What does your position tell you?**
Acting first is a disadvantage — you commit before seeing what others do.
Acting last is an advantage. With everyone still to act behind you, play
tighter than you would with only one or two players left. Being closer to the
button, or having fewer players left to act, both widen what's reasonable to
play.

**3. What does the stack depth allow?**
Compare the effective stack (the smaller of your stack and your opponent's)
to the pot. A big stack relative to the pot means there's room to build a
hand over multiple streets — don't rush decisions or commit everything at
once without reason. A small stack relative to the pot means the hand is
effectively already decided by a single bet or two — don't leave a
meaningful fraction of a short stack behind when you're already committed to
playing the pot.

**4. What has actually happened in the hand?**
Base your read only on real actions taken by real players in this hand — not
on a general vibe of "someone might be strong." A single limp is not
aggression. A single raise from one player is not "the whole table is
aggressive." Don't react to pressure that hasn't happened yet.

**5. Given all of the above, where is there room for your character to
express itself?**
Most hands have more than one defensible action. Where several options are
all reasonable given steps 1–4, let personality decide among *those*
options — a cautious character takes the more conservative reasonable line,
an aggressive character takes the bolder reasonable line. Personality should
never be the reason you take an action that steps 1–4 rule out. If your
character's instinct conflicts with what the pot odds, position, and stack
depth clearly call for, the character can *comment* on that tension in the
justification, but the action should still follow the math — a disciplined
character overriding their own impulse is more interesting to watch than a
character making a mathematically nonsensical play.

---

## Sizing

When betting or raising, default to a size between half the pot and the full
pot, or roughly 2.5–3x the previous bet if reopening preflop action. Smaller
or larger sizes should reflect something specific about the hand or the
character's style, not be arbitrary. Avoid sizes that leave an awkward
fraction of a short stack behind — if a bet would commit most of your
remaining chips anyway, consider committing all of them instead.

## Things to avoid

- Don't fold because a hand merely isn't the strongest possible hand — fold
  because it's unlikely to be best *given the specific action in front of
  you*.
- Don't treat "no one has raised" the same as "someone has raised."
- Don't call a large bet planning to fold to the next one unless you have a
  real reason to expect the hand will improve.
- Don't let the justification sentence argue for a different action than the
  one you actually take.

## Output discipline

Decide the action first, internally, using steps 1–5. Write the
justification second, so it reflects the decision rather than talking
yourself into one. The justification should reveal *why this character*
reached this action, not re-explain poker theory.

# Specific Strategy

## Types of Fish            (Grinder's Manual excerpt)
Types of Fish
There are four broad types of Fish that Hero will encounter on his poker journey. There are, of
course, sub-types of each of these and every individual player has some subtle differences from the
next, but with the limited information available to us at the virtual felt, it's necessary to group these
weaker opponents into four main categories. Our fold equity greatly depends upon which type of Fish
has limped or is left to act behind us in these situations and this categorisation should come in handy
throughout the rest of the manual in a variety of other situations.
Type A - The Fit-or-fold Fish: This is the bread and butter target of our ISO raises.
Identification: This type of Villain will play anything from a medium to wide range of hands pre-flop
usually entering the pot by limping. Sometimes he'll limp and fold to an ISO pre-flop or other times
limp/call and then fold frequently to a flop c-bet. Type A Fish have VPIP/PFR ratios like 40/6 and
34/11 - generally there is a large gap between the two stats. These stats don't take very long to tell the
true story and so Hero can identify this player quickly. This player will also have a fairly high fold to
c-bet stat of somewhere between 55% and 75%.
Exploitation: Hero can print money vs this player's limps by raising a wide range of hands,
especially in position, and then c-betting most flops expecting to have a lot of fold equity. The mantra
when playing against this type of player is simple: build it up, take it down! Hero inflates the pot to
then pick it up when his opponent plays too wide of a range pre-flop and subsequently gives up the
pot when he doesn't flop well, which will be most of the time.
Type B - The Station Fish: 'Station' is short for 'calling station', a common expression to describe
players who generally hate hitting the fold button. This is another loose passive player, but one
against whom Hero can't expect to generate too much fold equity. He calls much more than the fit-or-
fold Fish on all streets.
Identification: Pre-flop, the station Fish is relatively similar to the fit-or-fold Fish. Both players will
limp anything from a medium to a wide range, though the station Fish is more likely to have ridiculous
stats such as 90/15 or 65/3. While the fit-or-fold Fish will sometimes limp/fold before the flop, the
station Fish will almost never do this. Instead he'll call ISOs with close to his whole limping range
and then become very attached to any remote piece of the board he hits post-flop. Station Fish will
have much lower fold to c-bet stats, usually of 45% or less.
Exploitation: Hero no longer has the luxury of ISOing an extremely wide range. As his primary aim
has shifted from getting post-flop fold equity to simply value betting against a player who doesn't
want to fold. Hero should therefore adapt his pre-flop ISO range accordingly and seek to isolate this
player with higher frequent strength. As fold equity decreases, required frequent strength increases;
this relationship is the heart of the ISO triangle. Hero's plan is to isolate a stronger range and then
value bet like crazy when he connects well with the flop.
Type C - The Aggro Fish: 'Aggro' is online poker player slang for 'aggressive'. Thankfully for Hero,
the aggression is normally ill selected, over the top and easy to deal with, especially where Hero has
position.
Identification: This type of opponent opens the pot far more frequently than the previous two do. His
stats will normally converge at something like 57/38 or 44/23. When this player limps, his range will
normally be extra-weak as he would raise with many of the hands the last two Fish types limped. He
will basically never limp/fold and may even have the play of limp/raising in his arsenal. Post-flop
this player will have a very low fold to c-bet and will very often take lines like min-raising against c-
bets and frequently bluffing with zero to little equity post-flop.
Exploitation: Hero is even less able to realise fold equity against this player than he is against the
Station Fish as this player will call with just as many hands and also raise complete air when he feels
like it. As a result, Hero again needs to make sure that he has enough frequent strength in his ISO
range to carry out his plan of getting value post-flop from Villain's inability to fold any piece of the
board. Hero requires more regular showdown value to punish this type of Fish for his ill-timed bluffs.
Type D - The Whale: A Whale is more of a magnitude of Fish than a type, but one against whom
Hero's plan shifts somewhat.
Identification: In the animal kingdom, a whale is mammal, not a giant Fish; but for our poker
purposes, a giant fish is exactly what this player is. A whale tends to play an absurd amount of hands
pre-flop and make frequent serious errors. He might do things that appear financially suicidal like
shove for 100BB pre-flop with ATo or call down with king-high for three streets. His stats will
usually be miles out of line, for example, 95/80 or 71/4. He will fold very rarely and refuse to fold in
spots where anything else is ridiculous. Other players will share the hands they've played against him
with each other purely for amusement purposes. In reality, a Whale is just a player with a very poor
understanding of the game, who plays purely for fun and tends not to think very much if at all about
how to play well.
Exploitation: Now we reach an exception to our usual ISO strategy. Normally, we tighten our range
in the face of low fold equity as per the teachings of the ISO triangle. This player however, is so
abysmal and makes such gargantuan errors, that Hero needs to simply take every opportunity to
isolate him where his frequent strength is anywhere close to reasonable. The value of being the player
at the table to capitalise on these huge errors first is so immense, that having to bloat a few pots to
miss and give up post-flop is a small price for Hero to pay. Against whales, Hero should look to ISO
a very wide range indeed, especially in position, and have a very straightforward value orientated
game post-flop. The money will then cascade in his direction.

## The Check-Raise          (Exploitative Play excerpt)

We’re not going to spend time flatting three-bets out of position and check-raising. In my lessons, that situation seldom arises. People do not three-bet enough to justify the play 90% of the time. The last live database I looked at had such a small three-bet percentage that the note taker considered not keeping the stat anymore. The few people who do obsessively three-bet can be broken with a solid slowplay strategy and a tighter opening range.

We’re going to focus on check-raising from the big blind, because it is still an effective play. For one, make sure you’re calling raises that don’t go beyond 2.75x the big blind. If there are antes you can go up to 3.25x, but you need to know that you can check-raise the villain on most boards. The way you will know that is by identifying someone who opens too much and continuation-bets too much. Fortunately for us, this player is not too hard to find in today’s games. Any player opening from the lojack or later these days is statistically more likely to be opening 20%+ of the hands than not. 20% of hands is extremely difficult to defend postflop. You miss most boards with those hands. Beyond that, the steps are simple. The key factors required to check-raise someone from the blinds are:
♦ Someone opening too much (any player you have previously identified for ‘targeting’).
♦ Someone continuation-betting too much (practically every player on earth).
♦ A board worthy of check-raising (anything without two Broadway cards, especially those including a ten; generally not complete “chicken” boards, i.e. ultra-dry boards, usually featuring a pair).

Let me expand on these points.
You need someone to have too many hands. If a guy only opens A-A, he’s not going to be missing too many boards. However, most normal people hate folding, so they open a little too much. This is especially pronounced if it’s folded around to late position. Practically every player continuation-bets too much versus a player who completed from the big blind and checked the flop. The in-position player assumes that the big blind player has flatted with a wide array of hands due to the reduced price, and has largely missed the board. If you imagine having J♦-9♥ as the preflop raiser on a K♣-8♣-2♦ board, it would be strange to check back versus a big blind who just completed a bet and then checked. In general, it’d be an awful idea. Most of the time, the big blind is folding, and your bet turns a profit. For this reason, naturally, many players have learned to continuation-bet whenever they miss the board. This generally represents 50-60% of their range (no pair, no draw).
However, if they have 10♣-10♦ on that same board or K-10, perhaps they’ve been check-raised before, and they don’t feel like they want to play a big pot with one pair. So, they check, assuming the other player will bluff one or two streets. For this reason, most players’ continuation-betting ranges are competent, capable of controlling pot size, and they allow for many successful continuation-bet bluffs. They are also gloriously exploitable for the few tens of thousands who will read a book such as this one. Because we can see, looking at that range, that it’s two-pair or better and nothing. And there’s many more combinations of nothing than “two-pair or better”.
Finally, there are more boards you should be check-raising than boards you shouldn’t. The one board I tell everyone to lay off of is the two Broadway card board with one 10. A board like K-10-x or Q-10-x has so many Broadways and solid pairs in a person’s continuation-betting range that it makes it difficult to bluff. If there are just two Broadway cards, such as Q-J-3, that is a bit more viable, but it still allows your continuation-betting opponent to have a number of solid pairs. Ace high boards are also especially dangerous, since the vast majority of your opponent’s combinations are going to be A-x unpaired hands.
The boards that are great for check-raise bluffing are boards with one high card and two low cards, featuring a draw. On that board, you would be check-raising sets and two-pairs for value as well as draws. Due to the number of viable hands you could have, many players will just pitch their weak second pairs, not wanting to deal with you. That means you’ve secured a fold 70% of the time. Co-ordinated boards where your opponent will bet/fold one pair are money in the bank, generally speaking. Take a board such as K♠-8♠-2♠. If you have a disciplined opponent, you can check-raise large here, and they’ll generally show you an offsuit K-J and fold. That means they’re bet folding most of their K-10, K-9s, K-8s, Q-Q, J-J, 10-10, 9-9, 10-8, 9-8, and 8-7 combinations as well. That’s a lot of folding!


# Reference Hands

These are worked examples of sound decision-making using concepts outlined above. Attend to the reasoning pattern (how position, stack depth, and opponent type combine into a decision) rather than word choice and emotional tone.

REFERENCE HAND #1.

$1-3 at Stones Gambling Hall.
Dealt to Hero [LJ] ($785), NorCal Poker:

7c 9c

Hero [LJ]: Bet $20.
CO: 3-bet 55 w/ 600.

With my stack size over 250 big blinds, I'm deep-stacked enough to call here.
Hero [LJ]: Call $55.

Flop ($110):

Ad 8d 6s

Hero [LJ]: Check.
CO: Check.

Turn ($110):

Ad 8d 6s 3s

Hero [LJ]: Bet $50.
CO: Call.

River ($110):

Ad 8d 6s 3s 4c

Hero [LJ]: Bet $120.
CO: Raise $270.
Hero?

I think it's safe to say that I officially fell for his trap. I just never see him folding pocket aces or ace king if I go all in. The only thing to do is fold.

fold

REFERENCE HAND #2.

$1-3 at Stones Gambling Hall.
Dealt to Hero [BB] ($455), NorCal Poker:

Jc Js

EP: Open $25.
BTN: Call $25.
SB: Call $25 w/ 700.

EP has opened for the first time in an hour. I need to proceed with caution.

Hero [BB]: Call $25.

Flop ($100):

Jd 6h 4h

SB: Check.
Hero [BB]: Check.
EP: Bet $50.
SB: Call.
Hero?

If I was heads up with a short stack, I'd call. But because the SB has me covered, I'll raise to set up a jam on the turn.

raise 70

REFERENCE HAND #3.

$1-3 at Stones Gambling Hall.
Dealt to Hero [CO] ($560), NorCal Poker:

Ac Jh

Two limpers.
Hero [CO]: Raise $15.
BTN: Call $15.
SB: Call $15 w/ $190.
EP: Call $15.

Flop ($65):

Kc 8d 7d

SB: Check.
EP: Check.
BTN: Check.
Hero?

We've got nothing. Even though the king is better for our range than theirs, bluffing into three people with not even a draw is basically lighting money on fire.

check

REFERENCE HAND #4.

$1-3 at the Wynn.
Dealt to Hero [UTG] ($685), Aero Innovations:

8c Ac

Hero [UTG]: Open $8.
HJ: Call $8.
CO: Call $8.
BB: Call $8.

Flop ($33):

4d 8d 8s

BB: Check.
Hero [UTG]: Bet $10.
HJ: Fold.
CO: Call $10.
BB: Call $10.

Turn ($63):

4d 8d 8s 9c

BB: Check.
Hero?

The two callers are capped to weaker pairs and draws. Let's give them a bad price to deny their equity.

bet 50

REFERENCE HAND #5.

6-handed, $1-3 at the Wynn.
Dealt to Hero [UTG] ($300), Aero Innovations:

Ah 3d

Hero?

If we raise here, we're only getting called by better. We'd end up out of position against hands that dominate us, and suffer heavily from reverse implied odds.

fold

REFERENCE HAND #6.

$1-3 at the Wynn.
Dealt to Hero [BB] ($705), Aero Innovations:

Js 6s

UTG: Straddle #6.
SB: Call $6.
Hero [BB]: Call $6.

Flop ($18):

9d Kh As

SB: Check.
Hero [BB]: Check.
UTG: Bet $15.
SB: Fold.
Hero?

Nothing to do here but fold.

fold

REFERENCE HAND #7.

$1-3 at the Wynn.
Dealt to Hero [SB] ($750), Aero Innovations:

Ad As

CO: Limp $3 as action player.
Hero [SB]: Bet $17.
BB: Call.
CO: Call.

Flop ($54):

2s 9d 2h

Hero?

We're conveniently blocking A2 on this polarizing flop. We have virtually nothing to be afraid of, and I want opponents to catch up on over-cards. Let's lay a trap by checking with intention to call.

check

# Response Format

A valid response consists of either:

- a JUSTIFICATION, then two blank lines, then an ACTION; or
- only an ACTION (when justification is omitted).

The words "JUSTIFICATION" and "ACTION" must never appear.

Justification is REQUIRED for:
- EVERY bet.
- EVERY call.
- EVERY raise.
- EVERY postflop fold.

ONLY omit the justification when:
1. Preflop with an obvious fold.
2. Postflop with an obvious check.

## Justification

- Stay in character.
- Use simple language with personality.
- Avoid clichés.
- Do not use action asterisks.
- Avoid repetition.
- Comment only on what has changed since the most recent thought in the Context.
- The less interesting the action, the shorter the justification.
- Most justifications are short.
- Watch your token budget, because it's sparse.

## Action

- Choose an action from the responses listed at the end of the Context.
- Consist of at most one word and one number.
- Use no punctuation.

# Context
"""

# Information to help the AI reason.
def build_heuristics(hole_cards, community_cards):
    # Current hand
    heuristics = "\n"
    if(len(community_cards) == 0):
        return ""
    hand = Hand.classify(list(hole_cards), list(community_cards))
    heuristics += f"Your current hand: {hand.hand_id}\n"
    # How good is our pair?
    if(hand.hand_id == 'one pair'):
        paired_rank = hand.pairs[0][0].rank
        # Check if the pair belongs to me.
        hole_ranks = [card.rank for card in hole_cards]
        belongs_to_me = paired_rank in hole_ranks

        ranks_higher = 0
        if belongs_to_me:
            ordered = Hand.make_consecutive(community_cards, reversed=True)
            current_index = 0
            while(
                Deck.RANKS.index(ordered[current_index].rank) > \
                Deck.RANKS.index(paired_rank)):
                ranks_higher += 1
                current_index += 1
                if(current_index >= len(ordered)):
                    break
            on_board = paired_rank in [card.rank for card in ordered]
            if(ranks_higher == 0 and not on_board):
                heuristics += "You have an overpair to the board.\n"
            elif(ranks_higher == 0 and on_board):
                heuristics += "You have top pair.\n"
            elif(ranks_higher == 1):
                heuristics += "You have second pair.\n"
            elif(ranks_higher == 2):
                heuristics += "You have third pair.\n"
            else:
                heuristics += "You have a lousy pair.\n"

    # Paired board?
    rank_count = {}
    for card in community_cards:
        rank_count[card.rank] = rank_count.setdefault(card.rank, 0) + 1
    max_count_of_one_rank = max(rank_count.values())
    ranks_seen = len(rank_count.keys())
    if (len(community_cards) - ranks_seen == 2) and max_count_of_one_rank == 2:
        heuristics += "It's a double-paired board.\n"
    elif(max_count_of_one_rank == 2):
        heuristics += "The board is paired.\n"
    elif(max_count_of_one_rank == 3):
        heuristics += "There's trips on the board.\n"
    elif(max_count_of_one_rank == 4):
        heuristics += "There's quads on the board. Highest kicker wins.\n"
    else:
        heuristics += "The board is not paired.\n"

    # Flushes on the board?
    suit_count = {}
    for card in community_cards:
        suit_count[card.suit] = suit_count.setdefault(card.suit, 0) + 1
    two_suited = len(suit_count) == 2
    three_to_a_flush = max(suit_count.values()) == 3
    four_to_a_flush = max(suit_count.values()) == 4
    rainbow_flop = len(community_cards) == 3 and len(suit_count) == 3
    complete_rainbow = len(community_cards) >= 4 and len(suit_count) == 4
    if complete_rainbow:
        heuristics += "Complete rainbow board; no flushes possible.\n"
    elif rainbow_flop:
        heuristics += "Rainbow flop.\n"
    elif four_to_a_flush:
        heuristics += "There's four to a flush on the board.\n"
    elif three_to_a_flush:
        heuristics += "There's three to a flush on the board.\n"
    elif two_suited:
        heuristics += "There could be flush draws out there.\n"
  
    # Straights on the board?
    name = ""
    if len(community_cards) == 3:
        name = "data/straight_rough_count_flop.json"
    elif len(community_cards) == 4:
        name = "data/straight_rough_count_turn.json"
    elif len(community_cards) == 5:
        name = "data/straight_rough_count_river.json"

    if name != "":
        straight_counts = {}
        with open(name, "r") as file:
            straight_counts = json.load(file)
            combos = estimate_straight_combos(community_cards)
            samples = sum(straight_counts.values())
            sorted_counts = sorted(straight_counts.keys())
            cumul = 0
            for key in sorted_counts:
                key = int(key)
                if(key >= combos):
                    break
                cumul += int(straight_counts[str(key)])
            
            if(cumul/samples > 0.4):
                heuristics += f"The board is more connected than ~{round(cumul/samples*100, 2)}%  of boards at this street."
            elif(combos == 0):
                heuristics += "No made straights are currently possible."
            else:
                heuristics += f"A straight is at least theoretically possible.\nThe board is more connected than ~{round(cumul/samples*100, 2)}% of boards at this street.\n"

    return heuristics


def build_personality(player: Player):
    p = player.personality

    return f"""
\nAs {player.name}, you are {p.traits}. \
Your No-Limit Hold 'Em playstyle is {p.style}. \

Here's what your voice sounds like: 

- {'\n- '.join([quote for quote in p.quotes])}
"""

def build_prompt(round: HoldemRound, player: Player, bet_occurred: bool, highest_bet: float, min_raise: float):
        """
        CASES
        1. bet, check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind?
                Yes
        2. bet (all in), check, fold
            Has anyone else bet this street?
                No
            Can I afford to bet more than a big blind?
                No
            
        3. call (all in), fold
            Has anyone else bet this street?
                Yes
            Does the previous bettor have me covered?
                Yes

        4. raise (all in), call, fold
            Has anyone else bet this street?
                Yes
            Does the previous bettor have me covered?
                No
            Can I min raise with chips to spare?
                No

        5. raise, call, fold
            Has anyone else bet this street? 
                Yes
            Does the previous bettor have me covered?
                No
            Can I min raise with chips to spare?
                Yes
        """

        prev_highest_bet = highest_bet
        amount_to_call = prev_highest_bet - player.amount_in_street
        """Betting / Checking logic"""
        # Has anyone else bet this street?
        prev_bet_exists = bet_occurred
        # Can I afford to bet more than the minimum bet?
        can_afford_min_bet = player.chips > min_raise
        """Raising / Calling logic"""
        # Does the previous bettor have me covered?
        am_covered = amount_to_call >= player.chips
        # Can I min raise with chips to spare?
        can_raise_with_surplus = amount_to_call + min_raise < player.chips


        is_bet_check = (not prev_bet_exists) or (player.amount_in_street == prev_highest_bet)

        only_all_in_bet = (not prev_bet_exists) and (not can_afford_min_bet)
        only_all_in_call = prev_bet_exists and am_covered
        only_all_in_raise = prev_bet_exists and (not can_raise_with_surplus)

        bet_or_raise = "bet" if is_bet_check else "raise"
        check_or_call = "check" if is_bet_check else "call"
        fold_option = "" if is_bet_check else "fold"

        bet_all_in = "(all in)" if only_all_in_bet else ""
        call_all_in = "(all in)" if only_all_in_call else ""
        raise_all_in = "(all in)" if only_all_in_raise else ""

        bet_or_raise_all_in = bet_all_in or raise_all_in

        bet_or_raise_option = "" if call_all_in else f'''"{bet_or_raise} N" {bet_or_raise_all_in}\n'''

        return f"""\nIt's your turn to act.\n\n\
You've been dealt {player.hole_cards} in {player.position}.\n\
There's ${round.pot_queue.total_amount} in the pot.\n\
You have ${player.chips} in chips.\n\

{build_heuristics(player.hole_cards, round.community_cards)}

Choose from the following responses:
{check_or_call} {call_all_in}
{fold_option}
{bet_or_raise_option}
"""


def build_log(round: HoldemRound, perspective: Player | None = None, short_term_memory_limit=30) -> str:
    actions = round.actions
    if(len(actions) > short_term_memory_limit):
        surplus = len(actions)-short_term_memory_limit
        actions=actions[surplus:]

    log_string = ""

    prev_action_word = ""

    headers = set()

    for action in actions:
        phase = action.snapshot.phase
        round_id = action.snapshot.round_id
        subject_id = action.snapshot.subject_id
        # Headers
        header_string = f"{phase.value.upper()} (Hand #{round_id})"
        if(header_string not in headers):
            log_string += f"\n\n{header_string}\n\n"
            headers.add(header_string)

        
        # Whitespace between actions of different types on game start.
        if (phase == Phases.GAME_START) and (prev_action_word != "") and (action.action != prev_action_word):
            log_string += "\n"
        prev_action_word = action.action
        
        perspective_exists = perspective is not None
        perspective_differs = perspective_exists and (subject_id != perspective.player_id)
    
        must_anonymize = perspective_differs and (action.subject_type != Subjects.DEALER)
        if must_anonymize:
            if action.action == Actions.THINK and action.snapshot.subject_id != perspective.player_id:
                continue
            action = Action.anonymize(action)
            
        log_string += f"{action}\n"
        action.action

    return log_string

def log_action(round: HoldemRound, action: str, typed_object: T, object: str | None = None, subject_id:str = Subjects.DEALER_ID) -> HoldemRound:

    if object == None:
        object = str(typed_object)

    subject_type = Subjects.DEALER
    subject = Subjects.DEALER

    if(subject_id != Subjects.DEALER_ID):
        subject_type=Subjects.PLAYER
        subject = round.players[subject_id].name

    action_hash = f"{subject.replace(' ', '')}_{action}_{get_nanoseconds()}"
    if action==Actions.THINK or action==Actions.SAY:
        # Generate speech files for relevant actions.

        voice_index = 14
        voice_name = None
        if subject_id != Subjects.DEALER_ID:
            voice_index = round.players[subject_id].personality.voice_index
            voice_name = round.players[subject_id].personality.name

        generate_speech(
            round,
            typed_object,
            action_hash,
            voice_index=voice_index,
            voice_name=voice_name,
        )

        # Now that speech has been generated, we can trim this.
        typed_object = typed_object.split('\n\n')[0]

    snapshot = Snapshot(
        typed_object=typed_object, 
        phase=round.phase, 
        round_id=round.round_id,
        pot_queue=round.pot_queue,
        community_cards=copy.deepcopy(round.community_cards), 
        players=copy.deepcopy(round.players), 
        seats=round.seats,
        time=get_time(), 
        subject_id=subject_id
        )

    new_action = Action(
        action_hash=action_hash,
        subject_type=subject_type, 
        subject=subject, 
        action=action, 
        object=object, 
        snapshot=snapshot
        )

    action_list = round.actions
    action_list.append(new_action)

    round = update(round, actions=action_list)
    save_game(round)

    return round

def init_rand(round, seed=None):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    random.seed(seed)
    round = log_action(round, Actions.SHUFFLE, seed)
    return round

def shuffle(l):
    random.shuffle(l)
    return l

def refresh_players(round: HoldemRound) -> HoldemRound:
    updated_players = {}
    updated_seats = [-1, -1, -1, -1, -1, -1]

    # Reset players' values
    for player in round.players.values():

        updated_player = Player(
            player_id=player.player_id,
            name=player.name, 
            position=Positions.NONE, 
            personality=player.personality, 
            hole_cards=[], 
            chips=player.chips, 
            amount_in_street=0, 
            amount_in_round=0,
            has_folded=False, 
            is_all_in=False,
            prev_id=-1,
            next_id=-1
        )
        updated_players[player.player_id] = updated_player
        # Populate updated player in same seat.
        seat_index = round.seats.index(player.player_id)
        updated_seats[seat_index] = updated_player.player_id
    

    return update(round, players=updated_players, seats=updated_seats)
    
def set_positions(round: HoldemRound) -> HoldemRound:
    round = update(round, seat_index_of_btn=(round.seat_index_of_btn + 1) % len(round.seats))

    position_names = HoldemRound.POSITIONS_PER_PLAYERCOUNT[len(round.players)]

    updated_players = copy.deepcopy(round.players)

    # Find ID of btn
    btn_seat_index = round.seat_index_of_btn

    while round.seats[btn_seat_index] == -1:
        btn_seat_index +=1
        btn_seat_index %= len(round.seats)

    btn_id = round.seats[btn_seat_index]
    # For next time. Prevent this value from lagging behind when seats are empty.
    round = update(round, seat_index_of_btn = btn_seat_index) 
    btn_player = round.players[btn_id]


    players_in_seat_order = []

    for player_id in round.seats:
        # Seats can be empty.
        if(player_id == -1):
            continue
        players_in_seat_order.append(round.players[player_id])

    offset = players_in_seat_order.index(btn_player)

    for i in range(offset - len(players_in_seat_order), offset):
        player = players_in_seat_order[i]
        new_position = position_names[i - offset]
        new_next_id = players_in_seat_order[(i + 1)%len(players_in_seat_order)].player_id
        new_prev_id = players_in_seat_order[(i - 1)%len(players_in_seat_order)].player_id

        updated_players[player.player_id] = \
            update(player, position=new_position, next_id=new_next_id, prev_id=new_prev_id)

        round = update(round, players=updated_players)
        round = log_action(
            round=round,
            action=Actions.IS_POSITION,
            typed_object=new_position,
            subject_id=player.player_id
        )




    return update(round, players=updated_players)

def update_players(round: HoldemRound, players_to_update: list[Player]) -> HoldemRound:

    updated_players = round.players
    
    for player in players_to_update:
        updated_players[player.player_id] = player

    return update(round, players=updated_players)

def right_pot(round: HoldemRound) -> HoldemRound:

    pot_queue = round.pot_queue
    ids_to_bets = pot_queue.ids_to_bets
    right_pots = pot_queue.right_pots if len(pot_queue.right_pots) else [Pot({}, [], 0)]

    if(len(ids_to_bets) == 0):
        return round

    # At the end of each street, the dealer creates one side pot for each unique all-in stack size,
    # in order from smallest to largest. Each side pot contains the maximum number of chips that a
    # player of that stack size can win.
    
    # The remainder (shared by each person who bet the max bet size) goes into the main pot.
    # If the main pot has 1 player involved, then it's uncalled and will return to that player.
    # (This will be checked for at showdown.)

    # To right the pot, first we determine if a side pot must be created. 
    # Any of these two conditions may be met.

    # SIDE POT CONDITION 1. Same bet sizes among non-folded players
    # On all streets except showdown: Co-existence of all-in and non all-in players

    bet_sizes = [bet for bet in ids_to_bets.values()]
    unique_bet_sizes = set(bet_sizes)
    sorted_unique_bet_sizes = sorted(unique_bet_sizes)

    amount_this_street = sum(bet_sizes)

    non_folded_bet_sizes = [ids_to_bets[id] for id in ids_to_bets if not round.players[id].has_folded]
    unique_non_folded_bet_sizes = set(non_folded_bet_sizes)

    all_in_ids = []
    ids_in_action = []

    for player in round.players.values():
        if(player.is_all_in):
            all_in_ids.append(player.player_id)
            continue
        if(player.has_folded):
            continue
        ids_in_action.append(player.player_id)
    
    coexistence = len(all_in_ids) > 0 and len(ids_in_action) > 1 
    # ids_in_action > 1 because, e.g., one person with chips remaining has no more reason to bet.
    is_river = round.phase == Phases.RIVER
    condition_1_met = coexistence and (not is_river) # Last street means "chips left behind" no longer create side pots.
    all_same_bet_size = len(unique_non_folded_bet_sizes) == 1

    if all_same_bet_size:
        main_pot = right_pots[-1]
        main_pot = update(main_pot, ids_involved=list(ids_to_bets.keys()), amount=main_pot.amount + amount_this_street)

        list_to_concatenate = [main_pot]
        if condition_1_met:
            # What we called the main pot, above, is now a side pot.
            actual_main_pot = Pot(
                ids_involved=list(set([id for id in ids_in_action])), 
                winning_card_set=[],
                amount=0
            )
            list_to_concatenate = list_to_concatenate + [actual_main_pot]

        right_pots = right_pots[:-1] + list_to_concatenate
        pot_queue = update(pot_queue, right_pots=list(right_pots), ids_to_bets={})
        round = update(round, pot_queue=pot_queue)
        print("condition 1")
        print(ids_to_bets)
        print(right_pots)


        return round

    # SIDE POT CONDITION 2. Different bet sizes
    # The existence of differing non-folded bet sizes at street end implies that each smaller bet size must
    # belong to an all-in player and, therefore, must yield a side pot.

    copy_to_disburse = copy.copy(ids_to_bets) # Subtract from this one while iterating through the other one.

    # Create one side pot for each differing bet size with an all-in person in it.
    # TODO: Determine if the lowest side pot should update the values of the previous main pot?

    ids_removed = set()

    # EXAMPLE:
    # Iterating through bet sizes A, B, and C
    #
    #   A     B        C   
    # ##| <- P|ayer in |he blinds who folded
    # ##|#####| <- Shor|-stacked player who raised all-in 
    # ##|#####| <- Pers|n who called the all-in then folded to a 3-bet
    # ##|#####|########| <- Person who 3-bet
    # ##|#####|########| <- Stack leader cold-called
    #
    # Bet size A has the blind who folded.
    # Bet size B has one all-in and one caller who folded.
    # Bet size C has the two stack leaders.
    # 
    # So for every tier like A, where there's no one at that tier who's all-in,
    # we add it to dead money, then add dead money to the next eligible pot's tier.
    # 
    # i.e. For a side pot to be created at some bet size, there must be at least one 
    # player at that bet size who's all-in.

    main_pot = right_pots[-1]
    right_pots = right_pots[:-1]
    dead_money = main_pot.amount # add this to the next eligible pot

    for bet_size in sorted_unique_bet_sizes:

        bettors_of_this_size = [round.players[id] for id in ids_to_bets \
            if (ids_to_bets[id] == bet_size)]

        those_who_folded = [player for player in bettors_of_this_size \
            if player.has_folded]

        # Add this value (decremented by smaller bet sizes' side pots) 
        # for every player remaining in copy_to_disburse.
        id_of_a_bettor = bettors_of_this_size[0].player_id
        adjusted_amount = copy_to_disburse[id_of_a_bettor] # The equivalent of bet_size, but decremented.

        # Each player matches the covered player's stack.
        side_pot_size = len(copy_to_disburse.values()) * adjusted_amount + dead_money

        if len(those_who_folded) < len(bettors_of_this_size):
            side_pot = Pot(
                ids_involved=list(copy_to_disburse.keys()),
                winning_card_set=[],
                amount=side_pot_size
            )
            right_pots += [side_pot]
            dead_money = 0
        else:
            # Accumulate this for the next valid side pot.
            dead_money = side_pot_size

        for id in ids_to_bets:
            # Remove bettors_of_this_size from copy_to_disburse.
            # They will no longer participate in any future pots.
            if(round.players[id] in bettors_of_this_size):
                copy_to_disburse.pop(id)
                ids_removed.add(id)
                continue

            # Skip lower-stacked players
            elif id in ids_removed:
                continue

            # Subtract the difference from every remaining player.
            copy_to_disburse[id] -= adjusted_amount

    pot_queue = update(pot_queue, right_pots=right_pots, ids_to_bets={})
    round = update(round, pot_queue=pot_queue)
    return round

def update_pot(round: HoldemRound, amount: float, bettor_id: int) -> HoldemRound:
    ids_to_bets = round.pot_queue.ids_to_bets

    prev_bet = ids_to_bets.setdefault(bettor_id, 0)
    ids_to_bets[bettor_id] = prev_bet + amount

    updated_pot_queue = update( \
        round.pot_queue,
        ids_to_bets=ids_to_bets,
        total_amount=round.pot_queue.total_amount + amount
        )
    return update(round, pot_queue=updated_pot_queue)

def attempt_bet(round: HoldemRound, player: Player, attempted_amount: int, action: str) -> HoldemRound:
    actual_bet = min(attempted_amount, player.chips)
    updated_chips = player.chips - actual_bet
    updated_amount_in_street = player.amount_in_street + actual_bet
    updated_amount_in_round = player.amount_in_round + actual_bet
    updated_is_all_in = (updated_chips == 0)

    updated_player = update( \
        player, chips=updated_chips, \
        amount_in_street=updated_amount_in_street, \
        amount_in_round=updated_amount_in_round, \
        is_all_in=updated_is_all_in)

    round = update_players(round, [updated_player])
    round = update_pot(round, actual_bet, player.player_id)

    return round, actual_bet

def post_blinds(round: HoldemRound) -> HoldemRound:

    # Post blinds.
    sb = HoldemRound.SMALL_BLIND
    bb = HoldemRound.BIG_BLIND

    sb_id = -1
    bb_id = -1
    for player in round.players.values():
        if (player.position == "SB") or (len(round.players) == 2 and player.position == "BTN"):
            sb_id = player.player_id
        elif (player.position == "BB"):
            bb_id = player.player_id

    round, sb_actual = attempt_bet(round, round.players[sb_id], sb, Actions.POST)
    round = log_action(round=round, action=Actions.POST, typed_object=sb_actual, subject_id=sb_id)
    round, bb_actual = attempt_bet(round, round.players[bb_id], bb, Actions.POST)
    round = log_action(round=round, action=Actions.POST, typed_object=bb_actual, subject_id=bb_id)

    return round

def get_player_id_by_position(round: HoldemRound, position: str) -> int:
    id = -1
    for player in round.players.values():
        if player.position == position:
            id = player.player_id
    return id


def deal_hole_cards(deck: Deck, round: HoldemRound) -> tuple[Deck, HoldemRound]:
    updated_players = round.players
    btn_id = get_player_id_by_position(round, Positions.BTN)
    current_id = round.players[btn_id].next_id
    ids_seen = set()

    while(current_id not in ids_seen):
        current_player = round.players[current_id]
        deck, hole_cards = Deck.pop(deck, 2)

        # Potential issue: These actions are being logged with outdated round instances
        updated_players[current_player.player_id] = update(current_player, hole_cards=hole_cards)
        round = log_action(round, Actions.DEALT, typed_object=hole_cards, subject_id=current_player.player_id)
        ids_seen.add(current_id)
        current_id = current_player.next_id

    round = update(round, players=updated_players)

    # Now remove the nodes of those who were all-in after posting blinds
    player_keys = list(round.players.keys())
    for key in player_keys:
        if(not round.players[key].is_all_in):
            continue
        round = remove_node(round=round, player=round.players[key])

    round = update(round, players=updated_players)
    

    return deck, round

def remove_node(round: HoldemRound, player: Player) -> HoldemRound:

    my_id = player.player_id
    new_parent_id = player.prev_id
    new_child_id = player.next_id

    new_parent = update(round.players[new_parent_id], next_id=new_child_id)
    new_child = update(round.players[new_child_id], prev_id=new_parent_id)
    player = update(round.players[my_id], prev_id=-1, next_id=-1)

    round = update_players(round, [new_parent, new_child, player])

    return round

# For the action section of the response.
def interpret_response(response: str) -> tuple [str, float]:

    print(f"{response}")

    # If they didn't follow instructions, split it by \n\n and prune all but the last instance.
    if(len(response) > 15):
        response = response.split('\n\n')[-1]

    response = response.strip().lower().replace('*', '').replace('"', '')

    # Some models like replying with, say, "raise80" instead of "raise 80", 
    # so we need to split it by iterating backwards until we find the first non-number.
    val_string = ""
    digits = '1234567890'
    for i in range(len(response)):
        char = response[-1 - i]
        if char not in digits:
            break
        val_string = char + val_string
    
    response_string = response[: -1 * len(val_string)] if len(val_string) > 0 else response
    val = float(val_string) if val_string != "" else -1

    # Some models reply with "allin" or "all in".
    if("allin" in response_string) or ("all in" in response_string):
        response_string = "raise"
        val = math.inf

    return response_string, val

def send_prompt(personality: str, context: str) -> str:
    print(f"\n\n\n{context}\n")

    client = anthropic.Anthropic()
        # claude-opus-4-6 -> ~$0.10/min

    # Makes sure the guidelines are over the minimum cache threshold.
    """response = client.messages.count_tokens(
        model="claude-haiku-4-5",
        system=f"{GUIDELINES}",
        messages=[
            {
                "role": "user",
                "content": "test",
            }
        ]
    )
    print(response.json())
    exit()
    """

    print(GUIDELINES + personality + context)

    message = client.messages.create( 
        model="claude-haiku-4-5",
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": GUIDELINES,
                "cache_control": {"type": "ephemeral", "ttl": "1h"}
            }
        ],
        messages=[
            {
                "role": "user",
                "content": personality + context,
            }
        ]
    )
    u = message.usage
    if(u.cache_creation_input_tokens != 0):
        print(
            f"CACHE CREATION TOKENS SPENT. [cache] read={u.cache_read_input_tokens} "
            f"created={u.cache_creation_input_tokens} "
            f"uncached={u.input_tokens} "
            f"total={u.cache_read_input_tokens + u.cache_creation_input_tokens + u.input_tokens}"
        )
    
    return message.content[0].text

def prompt_stuff(round: HoldemRound) -> HoldemRound:
    phase = round.phase

    is_preflop = (phase == Phases.PREFLOP)
    bet_occurred = is_preflop
    total_players = round.players.values()

    # Attempt to skip action.

    active_players = []
    for player in total_players:
        if (not player.has_folded) and (not player.is_all_in):
            active_players.append(player)

    action_remains = len(active_players) > 1

    if not action_remains:
        return round

    # Get players by position.

    players_by_position = {}

    for player in total_players:
        players_by_position[player.position] = player
    
    # Big blind ends action preflop.
    last_to_act = players_by_position[Positions.BB]
    
    # Btn ends action all other streets.
    if phase != Phases.PREFLOP:
        last_to_act = players_by_position[Positions.BTN]
        # If BTN has folded we must find the nearest active player.
        ppp = HoldemRound.POSITIONS_PER_PLAYERCOUNT[len(total_players)]
        ppp_index = ppp.index(Positions.BTN) # Always 0
        while(last_to_act not in active_players):
            ppp_index -= 1
            prev_position = ppp[ppp_index]
            last_to_act = players_by_position[prev_position]

    first_id = last_to_act.next_id
    curr_id = first_id

    acted = set() # Flush this each time a player bets.

    highest_bet = 0 if not is_preflop else HoldemRound.BIG_BLIND
    min_raise = HoldemRound.BIG_BLIND

    starting_active_ids = set([player.player_id for player in active_players])
    folded_ids = set()
    all_in_ids = set()

    while(curr_id not in acted):
        # Keep this for the next time curr_id is -1, to trace where the error occurred.
        print(f"REQUESTING ACTION FROM {curr_id}: {round.players[curr_id]}\n\nDATA: {round.players}\n\n {round.seats}")
        player = round.players[curr_id]
        # Skip all-in and folded players
        if(player.is_all_in or player.has_folded):
            print(f"Warning. This child ({player.name}) should have been severed.")
            next_id = player.next_id
            next_player = round.players[next_id]
            print(f"Attempting to continue with {next_player}.")
            player = next_player
            continue


        # Check if everyone else has folded.
        if(len(set.difference(starting_active_ids, folded_ids)) == 1):
            return round



        log = build_log(round, player)

        guidelines = GUIDELINES
        personality = build_personality(player)
        prompt = build_prompt(round, player, bet_occurred, highest_bet, min_raise)
        
        context = log + prompt
        print("\n\nSENDING PROMPT.\n\n")
        response = send_prompt(personality, context)

        print(response)

        processed, value = None, None
        parts = response.split('\n\n', 1)
        if(len(parts) > 1):
            processed, value = interpret_response(parts[1])
            round = log_action(
                round = round,
                action=Actions.THINK,
                typed_object=parts[0],
                subject_id=player.player_id
            )
        else:
            processed, value = interpret_response(parts[0])

        bet_amount = 0

        if(Actions.BET in processed):
            action = Actions.BET
            bet_amount = value
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player, folded players, and all-in players need to act again.
            bet_occurred = True
        elif(Actions.RAISE in processed):
            action = Actions.RAISE
            raise_by = max(value, min_raise)
            bet_amount = highest_bet + raise_by - player.amount_in_street
            min_raise = raise_by
            acted = set([player.player_id]).union(folded_ids).union(all_in_ids) # Everyone but this player needs to act again.
            bet_occurred = True
        elif (Actions.CALL in processed):
            # Keep this in for now, for when call unexpectedly fails to yield an all-in...
            action = Actions.CALL
            bet_amount = highest_bet - player.amount_in_street

        elif ("check" in processed):
            action = Actions.CHECK
            bet_amount = 0

        else:
            action = Actions.FOLD
            bet_amount = 0

            player = update(player, has_folded=True, hole_cards = [])
            round = update_players(round, [player])
            folded_ids.add(player.player_id)

        if(bet_amount > 0):
            round, bet_amount = attempt_bet(round, player, bet_amount, action)
        player = round.players[curr_id]

        acted.add(player.player_id)

        highest_bet = max(highest_bet, player.amount_in_street)

        next_id = player.next_id

        if(player.is_all_in):
            all_in_ids.add(player.player_id)
            round = remove_node(round, player)
            

        if(player.has_folded):
            folded_ids.add(player.player_id)
            round = remove_node(round, player)

        round = log_action( \
            round=round, 
            action=action, 
            typed_object=bet_amount if action != Actions.RAISE else player.amount_in_street, 
            subject_id=player.player_id
            )

        print(f'{round.players[curr_id]} has ${player.chips} in chips left after the end of this action')
        curr_id = next_id

        stack_sanity_check(round)


    return round

def has_folded_out_(round: HoldemRound) -> bool:
    phase = round.phase
    is_showdown = phase == Phases.SHOWDOWN
    remaining = sum([1 for p in round.players.values() if not p.has_folded])
    return (remaining == 1)
    

def settle_pot(round: HoldemRound, folded_out=False):

    # Disable all-in tag at showdown
    if round.phase == Phases.SHOWDOWN:
        player_ids = round.players.keys()
        updated_players = {}
        for id in player_ids:
            player = update(round.players[id], is_all_in=False)
            updated_players[id] = player
        round = update(round, players=updated_players)
        

    pot = round.pot_queue

    if(folded_out):
        amount = round.pot_queue.total_amount
        winner = [p for p in round.players.values() if not p.has_folded]
        player = winner[0]
        player = update(player, is_all_in=False)
        player = update(player, chips=player.chips + amount)
        round = update_players(round, [player])

        pot_queue = update(round.pot_queue, total_amount=0)
        round = update(round, pot_queue=pot_queue)

        round = log_action(
            round=round,
            action=Actions.COLLECT,
            typed_object=amount,
            subject_id=player.player_id
        )
        return round


    right_pots = pot.right_pots
    shown_ids = set()
    pot_number = -1
    first_pot_was_uncalled = False
    while(len(right_pots) > 0):
        pot_number += 1
        current_pot = right_pots[-1]

        candidates = [round.players[id] for id in current_pot.ids_involved \
            if not round.players[id].has_folded]

        if(len(candidates) == 1 and (pot_number == 0)):
            # Uncalled
            first_pot_was_uncalled = True

            if(current_pot.amount == 0):
                continue

            player = update(candidates[0], chips=candidates[0].chips + current_pot.amount)
            round = update_players(round, [player])
            round = log_action(round, Actions.RETURN, current_pot.amount, subject_id=candidates[0].player_id)
            right_pots = right_pots[:-1]
            continue


        # Update right_pot to include winning hand's cards.
        winning_hands = Hand.find_winners(candidates, round.community_cards)
        winning_card_set = set()
        for hand in winning_hands:
            for card in hand.cards:
                winning_card_set.add(card)
        
        current_pot = update(current_pot, winning_card_set=list(winning_card_set))
        right_pots[-1] = current_pot
        updated_pot_queue = update(round.pot_queue, right_pots=right_pots)
        round = update(round, pot_queue = updated_pot_queue)

        # Disburse winnings
        amount_per_winner = current_pot.amount/len(winning_hands)
        
        for hand in winning_hands:
            player = hand.player
            if(player in shown_ids):
                continue
            player = hand.player
            round = log_action(round, Actions.SHOW, player.hole_cards, \
                    object=f"{player.hole_cards} ({hand.hand_id})", subject_id=player.player_id)
            shown_ids.add(player.player_id)
        
        for hand in winning_hands:
            player = hand.player
            player = update(player, chips=player.chips + amount_per_winner)
            round = update_players(round, [player])

            action = Actions.COLLECT_SIDE

            if (pot_number == 0 and (not first_pot_was_uncalled)) or \
            pot_number == 1 and first_pot_was_uncalled:
                action = Actions.COLLECT

            pot_queue = update(round.pot_queue, total_amount=round.pot_queue.total_amount - amount_per_winner)
            round = update(round, pot_queue=pot_queue)


            round = log_action(round, action, amount_per_winner, subject_id=player.player_id)
        right_pots = right_pots[:-1]
    return round

def remove_seat_by_id(seats: list[int], id: int):
    return list([seat if seat != id else -1 for seat in seats])


def remove_empty_stacks(round:HoldemRound) -> HoldemRound:
    updated_players = {}
    player_keys = list(round.players.keys())
    updated_seats = []
    for key in player_keys:
        player = round.players[key]
        if(player.chips == 0):
            updated_seats = remove_seat_by_id(round.seats, player.player_id)
            round = update(round, seats=updated_seats)
            round = log_action(round=round, action=Actions.EXIT, typed_object=None, subject_id=player.player_id)
            continue
        updated_players[player.player_id] = player
    return update(round, players=updated_players)

def stack_sanity_check(round: HoldemRound):
    sum = 0
    for player in round.players.values():
        sum += player.chips
    
    sum += round.pot_queue.total_amount
    expected = HoldemRound.MAX_BUY_IN*6
    if(sum == expected):
        return

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    log_string = build_log(round)
    print(log_string)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(f"Warning. Expected {expected} but got {sum}.")
    # exit()


def play_round(round: HoldemRound) -> HoldemRound:
    round = refresh_players(round)
    round = update(round, phase=Phases.GAME_START)
    # seed=1774796861768377 <- good one for quick testing
    round = init_rand(round)
    deck = shuffle(Deck.generate_deck())
    round = set_positions(round)
    round = post_blinds(round)
    deck, round = deal_hole_cards(deck, round)

    def play_street(round: HoldemRound, deck:list[Card], phase:str, cards_to_pop:int) -> HoldemRound:
        community_cards=round.community_cards

        round = update(round, phase=phase)

        if(cards_to_pop != 0):
            deck, added_cards = Deck.pop(deck, cards_to_pop)
            community_cards += added_cards
            round = update(round, community_cards=community_cards)
            object = str(community_cards) if cards_to_pop != 1 else \
                f"{community_cards[:-1]} [{community_cards[-1]}]"
            round = log_action(round=round, action=Actions.FLIP, \
                typed_object=community_cards, object=object)

        round = prompt_stuff(round)

        # Flush players' amounts in at the end of each street.
        updated_players = {}
        for player in round.players.values():
            id = player.player_id
            updated_players[id] = update(player, amount_in_street=0)
            continue
        round = update(round, players=updated_players)

        has_folded_out = has_folded_out_(round)
        

        if has_folded_out:
            round = update(round, phase=Phases.RESULT)
            round = settle_pot(round, folded_out=True)
        else:
            round = right_pot(round)

        return round, deck, has_folded_out

    round, deck, has_folded_out = play_street(round, deck, Phases.PREFLOP, cards_to_pop=0)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.FLOP, cards_to_pop=3)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.TURN, cards_to_pop=1)
    if(has_folded_out): return round

    round, deck, has_folded_out = play_street(round, deck, Phases.RIVER, cards_to_pop=1)
    if(has_folded_out): return round

    round = update(round, phase=Phases.SHOWDOWN)
    round = settle_pot(round, folded_out=False)
    
    round = remove_empty_stacks(round)

    
    log_string = build_log(round)
    print(log_string)
    return round



