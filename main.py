import yaml
from game_structs import Personality, Player, HoldemRound
from constants import Positions

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




if __name__ == "__main__":
    personalities = load_personalities('characters.yaml')
    player_pool = init_players(personalities)