from dataclasses import asdict
import json
from game_structs import HoldemRound
from pathlib import Path
import subprocess
from tts_engine import synthesize_to_wav
    

def generate_round_filename(round: HoldemRound):
    return f"{round.date}_{round.time.replace(':', '-')}"

def generate_speech(round, words, action_hash, voice_index=14, voice_name=None):
    raw_path = Path(f"speech/raw_{generate_round_filename(round)}___{action_hash}.wav")
    final_path = Path(f"speech/{generate_round_filename(round)}___{action_hash}.wav")

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    provider = synthesize_to_wav(
        words,
        raw_path,
        voice_index=voice_index,
        voice_name=voice_name,
    )

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", str(raw_path),
        "-ar", "44100",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(final_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    raw_path.unlink(missing_ok=True)
    return provider

def save_game(round: HoldemRound):
    data = [asdict(obj) for obj in round.actions]
    path = Path(f"saves/{generate_round_filename(round)}.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=4, default=lambda o: list(o) if isinstance(o, set) else str(o))
    return