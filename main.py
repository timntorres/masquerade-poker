import yaml
from datetime import datetime

from game_structs import Personality, Player, HoldemRound, PotQueue
from game_logic import play_round
from constants import Positions, Phases

import random
from utils import shuffle, get_time, update

def load_personalities(filename: str):
    with open(filename, 'r') as file:
        try:
            data = yaml.safe_load(file)
            characters = data['characters']
            personalities = []
            for character in characters:
                p = Personality(
                    character['id'],
                    character['name'],
                    character['traits'],
                    character['playstyle'],
                    character['quotes']
                )
                personalities.append(p)
            return personalities
        except yaml.YAMLError as exc:
            print(exc)
            exit()

def init_players(personalities: list[Personality]) -> list[Player]:
        players = []
        for personality in personalities:
            p = Player(
                player_id=personality.id,
                name=personality.name,
                position=Positions.NONE,
                personality=personality,
                hole_cards=[],
                # chips=random.choice([21, 27, 35]),
                chips=HoldemRound.MAX_BUY_IN,
                amount_in_street=0,
                amount_in_round=0,
                has_folded=False,
                is_all_in=False,
                prev_id=-1,
                next_id=-1
            )
            players.append(p)
        return players

def select_players(options: list[Player], count=6, ids:list[int]|None=None) -> dict[int, Player]:
    selected_players = {}

    if ids != None:
        ids_set = set(ids)
        for player in options:
            if(player.player_id in ids_set):
                selected_players[player.player_id] = player

        return selected_players
    shuffle(options)


    for i in range(count):
        player = options[i]
        id = player.player_id
        selected_players[id] = player

    return selected_players


def trim_action_list(round: HoldemRound) -> HoldemRound:
    action_list_trimmed = round.actions[40:] if len(round.actions) > 40 else round.actions
    return update(round, actions=action_list_trimmed)

def populate_seats(round: HoldemRound) -> HoldemRound:
    seats_ = list(round.players.keys())
    return update(round, seats=seats_)


if __name__ == "__main__":
    personalities = load_personalities('characters.yaml')
    player_pool = init_players(personalities)
    players = select_players(player_pool, ids=[3, 2, 11, 6, 1, 14])

    empty_queue = PotQueue(
        ids_to_bets={},
        total_amount=0,
        right_pots=[]
    )

    round = HoldemRound(
        phase = Phases.GAME_START,
        round_id = 0,
        time = get_time(),
        pot_queue=empty_queue,
        actions = [],
        players = players,
        seats = [],
        community_cards = []
    )

    
    round = populate_seats(round)
    while(len(round.players.values()) > 1):

        actions = round.actions
        if(len(actions) > 30):
            surplus = len(actions)-30
            round = update(round, actions=actions[surplus:])

        # Refresh pot
        empty_queue = update(empty_queue, ids_to_bets={}, total_amount=0, right_pots=[])

        round = update(round, pot_queue=empty_queue, community_cards=[], round_id=round.round_id+1)
        round = play_round(round)
        round = trim_action_list(round)

