from pathlib import Path

from .benchmark import _client


def synthesize_callback(
    workspace: Path,
    text: str,
    voice_id: str,
    output_path: Path,
    model_id: str = "eleven_multilingual_v2",
) -> Path:
    if not text.strip():
        raise ValueError("Provide the callback text in the target language.")
    if not voice_id.strip():
        raise ValueError("Provide a voice ID from your ElevenLabs voice library.")
    client = _client(workspace)
    audio_chunks = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_44100_128",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        for chunk in audio_chunks:
            stream.write(chunk)
    return output_path
