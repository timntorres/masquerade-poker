import yaml
from datetime import datetime

from game_structs import Personality, Player, HoldemRound, Pot
from game_logic import play_round
from constants import Positions

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
                chips=HoldemRound.MAX_BUY_IN,
                amount_in=0,
                has_folded=False,
                is_all_in=False,
                next_id_to_act=-1
            )
            players.append(p)
        return players

def select_players(options: str, count=6) -> dict[int, Player]:
    shuffle(options)

    selected_players = {}

    for i in range(count):
        player = options[i]
        id = player.player_id
        selected_players[id] = player

    return selected_players

def remove_empty_stacks(round:HoldemRound) -> HoldemRound:
    updated_players = {}
    for player in round.players.values():
        if(player.chips == 0):
            continue
        updated_players[player.player_id] = player
    return update(round, players=updated_players)

def trim_action_list(round: HoldemRound) -> HoldemRound:
    action_list_trimmed = round.actions[40:] if len(round.actions) > 40 else round.actions
    return update(round, actions=action_list_trimmed)

def populate_seats(round: HoldemRound) -> HoldemRound:
    seats_ = list(round.players.keys())
    return update(round, seats=seats_)


if __name__ == "__main__":
    personalities = load_personalities('characters.yaml')
    player_pool = init_players(personalities)
    players = select_players(player_pool)

    empty_pot = Pot(
            set(players.keys()),
            0,
            None
         )

    round = HoldemRound(
         list(players.keys())[0],
         0,
         get_time(),
         empty_pot,
         [],
         players,
         [],
         []
    )

    
    round = populate_seats(round)
    while(len(round.players.values()) > 1):
        round = play_round(round)
        round = remove_empty_stacks(round)
        round = trim_action_list(round)

        # Iterate position
        prev_btn = round.players[round.btn_id]
        next_btn_id = prev_btn.next_id_to_act
        update(round, btn_id = round.players[next_btn_id])

