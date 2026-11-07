import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mississauga_unheard.prototype import synthesize_callback
from elevenlabs.core.api_error import ApiError


class PrototypeTests(unittest.TestCase):
    def test_rejects_example_voice_id_before_api_call(self):
        with patch("mississauga_unheard.prototype._client") as client:
            with self.assertRaisesRegex(ValueError, "voice ID"):
                synthesize_callback(
                    Path("."), "Hello", "YOUR_VOICE_ID", Path("callback.mp3")
                )
            client.assert_not_called()

    def test_synthesizes_to_requested_file(self):
        def convert(**kwargs):
            self.assertEqual(kwargs["voice_id"], "test-voice")
            self.assertEqual(kwargs["model_id"], "eleven_multilingual_v2")
            return iter([b"audio-", b"bytes"])

        fake_client = SimpleNamespace(
            text_to_speech=SimpleNamespace(convert=convert)
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "callback.mp3"
            with patch("mississauga_unheard.prototype._client", return_value=fake_client):
                result = synthesize_callback(
                    Path(temporary), "مرحبا", "test-voice", output
                )
            self.assertEqual(result.read_bytes(), b"audio-bytes")
            self.assertEqual(result, output)

    def test_explains_voice_not_found_response(self):
        def convert(**kwargs):
            raise ApiError(
                status_code=404,
                body={
                    "detail": {
                        "code": "voice_not_found",
                        "message": f"Voice {kwargs['voice_id']} was not found",
                    }
                },
            )

        fake_client = SimpleNamespace(
            text_to_speech=SimpleNamespace(convert=convert)
        )
        with tempfile.TemporaryDirectory() as temporary:
            with patch("mississauga_unheard.prototype._client", return_value=fake_client):
                with self.assertRaisesRegex(RuntimeError, "real voice ID"):
                    synthesize_callback(
                        Path(temporary), "Hello", "not-a-voice", Path(temporary) / "out.mp3"
                    )


if __name__ == "__main__":
    unittest.main()
