from dataclasses import asdict
import json
from game_structs import HoldemRound
from pathlib import Path


def save_game(round: HoldemRound):
    data = [asdict(obj) for obj in round.actions]
    path = Path(f'saves/{round.date}_{round.time.replace(':', '-')}.json')
    path.parent.mkdir(parents=True, exist_ok=True)

    json_string = json.dumps(data, indent=4)
    with open(path, 'w')  as f:
        json.dump(data, f, indent=4, default=lambda o: list(o) if isinstance(o, set) else str(o))
    return