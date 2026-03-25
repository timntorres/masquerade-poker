import yaml
from datetime import datetime

from game_structs import Personality, Player, HoldemRound, Pot
from game_logic import play_round
from constants import Positions

from rand_manager import shuffle

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
                personality.id,
                personality.name,
                Positions.NONE,
                personality,
                [],
                HoldemRound.MAX_BUY_IN,
                0,
                False,
                False
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

if __name__ == "__main__":
    personalities = load_personalities('characters.yaml')
    player_pool = init_players(personalities)
    player_dict = select_players(player_pool)

    empty_pot = Pot(
            set(player_dict.keys()),
            0,
            None
         ),

    round = HoldemRound(
         0,
         datetime.now(),
         empty_pot,
         [],
         player_dict
    )

    round = play_round(round)
    
