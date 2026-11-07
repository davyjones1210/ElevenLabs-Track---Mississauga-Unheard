import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mississauga_unheard.benchmark import run_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_transcribes_small_local_sample_and_writes_wer_cer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dataset = root / "02_speech_home_languages_FLEURS"
            (dataset / "audio").mkdir(parents=True)
            (dataset / "audio" / "sample.flac").write_bytes(b"fake audio")
            with (dataset / "metadata.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=["file", "language", "transcription"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "file": "audio/sample.flac",
                        "language": "Urdu",
                        "transcription": "hello world",
                    }
                )

            fake_client = SimpleNamespace(
                speech_to_text=SimpleNamespace(
                    convert=lambda **kwargs: SimpleNamespace(text="hello")
                )
            )
            output = root / "outputs"
            with patch("mississauga_unheard.benchmark._client", return_value=fake_client):
                rows = run_benchmark(
                    root, output, root, ["fleurs"], 1, {"urdu"}
                )

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["wer"], "0.500000")
            self.assertEqual(rows[0]["cer"], "0.500000")
            self.assertTrue((output / "asr_summary.csv").is_file())


if __name__ == "__main__":
    unittest.main()
