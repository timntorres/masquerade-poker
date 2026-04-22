from dataclasses import asdict
import json
from game_structs import HoldemRound
from pathlib import Path
import subprocess
import pyttsx3
    

def generate_round_filename(round: HoldemRound):
    return f'{round.date}_{round.time.replace(':', '-')}'

def generate_speech(round, words, hash):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[14].id)

    raw_path = Path(f'speech/raw_{generate_round_filename(round)}___{hash}.wav')
    final_path = Path(f'speech/{generate_round_filename(round)}___{hash}.wav')

    raw_path.parent.mkdir(parents=True, exist_ok=True)

    engine.save_to_file(words, str(raw_path))
    engine.runAndWait()

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", str(raw_path),
        "-ar", "44100",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(final_path)
    ], check=True)

    raw_path.unlink(missing_ok=True)

def save_game(round: HoldemRound):
    data = [asdict(obj) for obj in round.actions]
    path = Path(f'saves/{generate_round_filename(round)}.json')
    path.parent.mkdir(parents=True, exist_ok=True)

    json_string = json.dumps(data, indent=4)
    with open(path, 'w')  as f:
        json.dump(data, f, indent=4, default=lambda o: list(o) if isinstance(o, set) else str(o))
    return