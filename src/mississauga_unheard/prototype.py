from pathlib import Path

from .benchmark import _client


def _api_error_message(error, voice_id: str) -> str:
    body = error.body
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, dict):
        code = detail.get("code") or detail.get("status")
        message = detail.get("message") or str(detail)
    else:
        code = None
        message = str(detail)

    if code == "voice_not_found":
        return (
            f"ElevenLabs could not find voice ID {voice_id!r}. Replace the example "
            "`YOUR_VOICE_ID` with a real voice ID from your ElevenLabs Voices page. "
            "If you already used a real ID, make sure that voice is available to this account."
        )
    return f"ElevenLabs text-to-speech request failed (HTTP {error.status_code}): {message}"


def synthesize_callback(
    workspace: Path,
    text: str,
    voice_id: str,
    output_path: Path,
    model_id: str = "eleven_multilingual_v2",
) -> Path:
    if not text.strip():
        raise ValueError("Provide the callback text in the target language.")
    voice_id = voice_id.strip()
    if not voice_id or voice_id.casefold() in {"your_voice_id", "<voice_id>"}:
        raise ValueError("Provide a voice ID from your ElevenLabs voice library.")
    client = _client(workspace)
    from elevenlabs.core.api_error import ApiError

    try:
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
    except ApiError as exc:
        raise RuntimeError(_api_error_message(exc, voice_id)) from exc
    return output_path
