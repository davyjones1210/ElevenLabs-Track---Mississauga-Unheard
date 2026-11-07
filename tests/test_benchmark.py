import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mississauga_unheard.benchmark import run_benchmark, run_paired_fleurs_benchmark
from mississauga_unheard.data import read_csv, write_csv


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

            def convert(**kwargs):
                self.assertEqual(kwargs["model_id"], "scribe_v2")
                self.assertTrue(kwargs["file"])
                return SimpleNamespace(text="hello")

            fake_client = SimpleNamespace(
                speech_to_text=SimpleNamespace(convert=convert)
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

    def test_paired_fleurs_reuses_cached_clips_and_transcribes_missing_languages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dataset = root / "02_speech_home_languages_FLEURS"
            audio = dataset / "audio"
            audio.mkdir(parents=True)
            (audio / "ar.flac").write_bytes(b"cached")
            (audio / "en.flac").write_bytes(b"new")
            with (dataset / "metadata.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=[
                        "file",
                        "language",
                        "fleurs_id",
                        "gender",
                        "duration_sec",
                        "transcription",
                        "raw_transcription",
                    ],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "file": "audio/ar.flac",
                            "language": "Arabic",
                            "fleurs_id": "1589",
                            "gender": "female",
                            "transcription": "مرحبا",
                            "raw_transcription": "مرحبا",
                        },
                        {
                            "file": "audio/en.flac",
                            "language": "English",
                            "fleurs_id": "1589",
                            "gender": "male",
                            "transcription": "hello",
                            "raw_transcription": "hello",
                        },
                    ]
                )
            output = root / "outputs"
            output.mkdir()
            write_cache = [
                {
                    "dataset": "fleurs",
                    "language": "Arabic",
                    "file": "audio/ar.flac",
                    "reference": "مرحبا",
                    "transcript": "مرحبا",
                    "wer": "0.000000",
                    "cer": "0.000000",
                    "reference_label": "",
                }
            ]
            write_csv(output / "asr_benchmark.csv", write_cache)
            calls = []
            fake_client = SimpleNamespace(
                speech_to_text=SimpleNamespace(
                    convert=lambda **kwargs: (
                        calls.append(kwargs)
                        or SimpleNamespace(text="hello", language_code="eng")
                    )
                )
            )
            with patch("mississauga_unheard.benchmark._client", return_value=fake_client):
                result = run_paired_fleurs_benchmark(root, output, root)

            self.assertEqual(len(result), 2)
            self.assertEqual(len(calls), 1)
            self.assertEqual({row["fleurs_id"] for row in result}, {"1589"})
            self.assertEqual(len(read_csv(output / "paired_fleurs_summary.csv")), 2)


if __name__ == "__main__":
    unittest.main()
