import os
import shutil
import subprocess
from pathlib import Path
import tempfile
from typing import Optional
import asyncio

try:
    import edge_tts
except ImportError:  # Optional dependency for higher-quality neural voices.
    edge_tts = None

try:
    import pyttsx3
except ImportError:  # Optional dependency when Piper is available.
    pyttsx3 = None


EDGE_DEFAULT_VOICES = [
    "en-US-AvaNeural",
    "en-US-AndrewNeural",
    "en-US-BrianNeural",
    "en-US-EmmaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-RogerNeural",
]

EDGE_CHARACTER_VOICES = {
    "Popeye": "en-US-RogerNeural",
    "Sherlock Holmes": "en-GB-RyanNeural",
    "Cheshire Cat": "en-GB-SoniaNeural",
    "Jay Gatsby": "en-US-AndrewNeural",
    "Dr. Henry Jekyll": "en-GB-RyanNeural",
    "Mr. Edward Hyde": "en-GB-ThomasNeural",
    "Cleopatra": "en-GB-SoniaNeural",
    "Frankenstein's Monster": "en-US-BrianNeural",
    "Dr. Victor Frankenstein": "en-US-GuyNeural",
    "Winnie the Pooh": "en-US-ChristopherNeural",
    "Eeyore": "en-US-EricNeural",
    "Tigger": "en-US-SteffanNeural",
    "Piglet": "en-US-AnaNeural",
    "Steamboat Willie": "en-US-AriaNeural",
    "Pinocchio": "en-US-GuyNeural",
    "Betty Boop": "en-US-AvaNeural",
    "Ebenezer Scrooge": "en-GB-RyanNeural",
}


def synthesize_to_wav(
    text: str,
    output_path: Path,
    voice_index: Optional[int] = None,
    voice_name: Optional[str] = None,
) -> str:
    """Generate speech to a WAV file using configured providers in priority order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    provider_order = os.getenv("MP_TTS_PROVIDER_ORDER", "").strip()
    if not provider_order:
        provider_order = "edge,piper,say,pyttsx3"

    providers = [
        provider.strip().lower()
        for provider in provider_order.split(",")
        if provider.strip()
    ]

    strict_humanlike = os.getenv("MP_TTS_STRICT_HUMANLIKE", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    neural_providers = {"edge", "piper"}

    errors: list[str] = []
    for provider in providers:
        try:
            if provider == "edge":
                if _synthesize_with_edge_tts(text, output_path, voice_index=voice_index, voice_name=voice_name):
                    if strict_humanlike and provider not in neural_providers:
                        errors.append(f"{provider} blocked by MP_TTS_STRICT_HUMANLIKE.")
                    else:
                        return "edge"
                errors.append("edge unavailable or failed.")
            elif provider == "piper":
                if _synthesize_with_piper(text, output_path, voice_index=voice_index, voice_name=voice_name):
                    if strict_humanlike and provider not in neural_providers:
                        errors.append(f"{provider} blocked by MP_TTS_STRICT_HUMANLIKE.")
                    else:
                        return "piper"
                errors.append("piper unavailable or misconfigured.")
            elif provider == "say":
                if _synthesize_with_macos_say(text, output_path, voice_index=voice_index):
                    if strict_humanlike:
                        errors.append("say blocked by MP_TTS_STRICT_HUMANLIKE.")
                    else:
                        return "say"
                errors.append("say unavailable or failed.")
            elif provider == "pyttsx3":
                if _synthesize_with_pyttsx3(text, output_path, voice_index=voice_index):
                    if strict_humanlike:
                        errors.append("pyttsx3 blocked by MP_TTS_STRICT_HUMANLIKE.")
                    else:
                        return "pyttsx3"
                errors.append("pyttsx3 unavailable or failed.")
            else:
                errors.append(f"Unknown provider '{provider}'.")
        except Exception as exc:  # Keep falling back through provider list.
            errors.append(f"{provider}: {exc}")

    joined = " | ".join(errors) if errors else "No providers configured."
    raise RuntimeError(f"Failed to synthesize speech. {joined}")


def _synthesize_with_piper(
    text: str,
    output_path: Path,
    voice_index: Optional[int] = None,
    voice_name: Optional[str] = None,
) -> bool:
    piper_bin = os.getenv("MP_TTS_PIPER_BIN", "piper")
    if shutil.which(piper_bin) is None:
        return False

    model_path = _resolve_piper_model(voice_index=voice_index, voice_name=voice_name)
    if model_path is None:
        return False

    subprocess.run(
        [
            piper_bin,
            "--model",
            str(model_path),
            "--output_file",
            str(output_path),
        ],
        input=text,
        text=True,
        check=True,
    )
    return output_path.exists()


def _resolve_piper_model(
    voice_index: Optional[int] = None,
    voice_name: Optional[str] = None,
) -> Optional[Path]:
    model = os.getenv("MP_TTS_PIPER_MODEL")
    if model:
        model_path = Path(model)
        if model_path.exists():
            return model_path

    model_dir = Path(os.getenv("MP_TTS_PIPER_MODEL_DIR", "voices"))
    if not model_dir.exists():
        return None

    candidates = sorted(model_dir.glob("*.onnx"))
    if not candidates:
        return None

    if voice_name:
        normalized = voice_name.lower().replace(" ", "_")
        for candidate in candidates:
            stem = candidate.stem.lower()
            if normalized in stem or voice_name.lower() in stem:
                return candidate

    if voice_index is not None:
        return candidates[voice_index % len(candidates)]

    return candidates[0]


def _synthesize_with_pyttsx3(text: str, output_path: Path, voice_index: Optional[int] = None) -> bool:
    if pyttsx3 is None:
        return False

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    if voices:
        index = (voice_index or 0) % len(voices)
        engine.setProperty("voice", voices[index].id)

    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    return output_path.exists()


def _synthesize_with_edge_tts(
    text: str,
    output_path: Path,
    voice_index: Optional[int] = None,
    voice_name: Optional[str] = None,
) -> bool:
    if edge_tts is None:
        return False

    selected_voice = _select_edge_voice(voice_index=voice_index, voice_name=voice_name)
    rate = os.getenv("MP_TTS_EDGE_RATE", "+0%")
    pitch = os.getenv("MP_TTS_EDGE_PITCH", "+0Hz")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3_path = Path(tmp.name)

    try:
        asyncio.run(_edge_save(text=text, voice=selected_voice, rate=rate, pitch=pitch, mp3_path=mp3_path))
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(mp3_path),
                "-ar",
                "44100",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(output_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return output_path.exists()
    finally:
        mp3_path.unlink(missing_ok=True)


async def _edge_save(text: str, voice: str, rate: str, pitch: str, mp3_path: Path) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(mp3_path))


def _select_edge_voice(voice_index: Optional[int] = None, voice_name: Optional[str] = None) -> str:
    if voice_name and voice_name in EDGE_CHARACTER_VOICES:
        return EDGE_CHARACTER_VOICES[voice_name]

    configured = [
        x.strip()
        for x in os.getenv("MP_TTS_EDGE_VOICES", "").split(",")
        if x.strip()
    ]
    candidates = configured if configured else EDGE_DEFAULT_VOICES

    if voice_index is None:
        return candidates[0]
    return candidates[voice_index % len(candidates)]


def _synthesize_with_macos_say(text: str, output_path: Path, voice_index: Optional[int] = None) -> bool:
    say_bin = shutil.which("say")
    if say_bin is None:
        return False

    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        aiff_path = Path(tmp.name)

    try:
        cmd = [say_bin, "-o", str(aiff_path), text]

        voices = _list_macos_voices(say_bin)
        if voices:
            selected = voices[(voice_index or 0) % len(voices)]
            cmd = [say_bin, "-v", selected, "-o", str(aiff_path), text]

        subprocess.run(cmd, check=True)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(aiff_path),
                "-ar",
                "44100",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(output_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return output_path.exists()
    finally:
        aiff_path.unlink(missing_ok=True)


def _list_macos_voices(say_bin: str) -> list[str]:
    result = subprocess.run(
        [say_bin, "-v", "?"],
        check=True,
        capture_output=True,
        text=True,
    )
    voices: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        voices.append(line.split()[0])
    return voices