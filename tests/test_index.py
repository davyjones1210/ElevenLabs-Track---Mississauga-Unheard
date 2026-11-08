import tempfile
import unittest
from pathlib import Path

from mississauga_unheard.data import write_csv
from mississauga_unheard.index import build_unheard_index


class IndexTests(unittest.TestCase):
    def test_uses_character_error_rate_and_audio_intent_when_available(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            derived = root / "01_people_census" / "derived"
            derived.mkdir(parents=True)
            write_csv(
                derived / "geo_language_long.csv",
                [
                    {
                        "geo_level": "ward",
                        "geo": "1",
                        "population_language_base": "200",
                        "knows_neither_english_nor_french": "10",
                        "pct_knows_neither_english_nor_french": "5.0",
                        "language": "Mandarin Chinese",
                        "home_speakers": "100",
                    },
                    {
                        "geo_level": "ward",
                        "geo": "1",
                        "population_language_base": "200",
                        "knows_neither_english_nor_french": "10",
                        "pct_knows_neither_english_nor_french": "5.0",
                        "language": "Urdu",
                        "home_speakers": "100",
                    },
                ],
            )
            output = root / "outputs"
            write_csv(
                output / "asr_benchmark.csv",
                [
                    {
                        "dataset": "fleurs",
                        "language": "Mandarin Chinese",
                        "wer": "1.0",
                        "cer": "0.0",
                    },
                    {"dataset": "fleurs", "language": "Urdu", "wer": "0.5", "cer": "0.2"},
                ],
            )
            write_csv(
                output / "paired_fleurs_summary.csv",
                [
                    {"language": "Mandarin Chinese", "cer": "0.2"},
                    {"language": "Urdu", "cer": "0.2"},
                ],
            )
            write_csv(
                output / "audio_intent_evaluation.csv",
                [
                    {
                        "language": "Mandarin Chinese",
                        "samples": "1",
                        "correct": "0",
                        "status": "audio transcript; exploratory sample",
                    },
                    {
                        "language": "Urdu",
                        "samples": "1",
                        "correct": "1",
                        "status": "audio transcript; exploratory sample",
                    },
                ],
            )

            result = build_unheard_index(root, output)[0]

            self.assertEqual(result["unheard_index"], "30.000")
            self.assertEqual(result["weighted_error_count_proxy"], "60.0")
            self.assertIn("FLEURS_CER", result["risk_sources"])
            self.assertIn("audio_intent_error", result["risk_sources"])


if __name__ == "__main__":
    unittest.main()
