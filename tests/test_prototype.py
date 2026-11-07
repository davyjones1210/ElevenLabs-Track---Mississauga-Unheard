import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mississauga_unheard.prototype import synthesize_callback


class PrototypeTests(unittest.TestCase):
    def test_synthesizes_to_requested_file(self):
        fake_client = SimpleNamespace(
            text_to_speech=SimpleNamespace(
                convert=lambda **kwargs: iter([b"audio-", b"bytes"])
            )
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "callback.mp3"
            with patch("mississauga_unheard.prototype._client", return_value=fake_client):
                result = synthesize_callback(
                    Path(temporary), "مرحبا", "test-voice", output
                )
            self.assertEqual(result.read_bytes(), b"audio-bytes")
            self.assertEqual(result, output)


if __name__ == "__main__":
    unittest.main()
