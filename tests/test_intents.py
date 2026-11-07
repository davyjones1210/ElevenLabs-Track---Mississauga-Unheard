import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mississauga_unheard.data import write_csv
from mississauga_unheard.intents import evaluate_audio_intents


class AudioIntentTests(unittest.TestCase):
    def test_routes_asr_transcript_and_writes_per_clip_confusion(self):
        training = {
            "minds14": [
                {"language": "English", "file": "train1.flac", "label": "pay_bill", "text": "pay my bill"},
                {"language": "English", "file": "train2.flac", "label": "pay_bill", "text": "pay this bill"},
                {"language": "English", "file": "train3.flac", "label": "freeze", "text": "freeze my card"},
                {"language": "English", "file": "train4.flac", "label": "freeze", "text": "freeze the card"},
            ],
            "massive": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            write_csv(
                output / "asr_benchmark.csv",
                [
                    {
                        "dataset": "minds14",
                        "language": "English",
                        "file": "test.flac",
                        "transcript": "please pay the bill",
                        "reference": "pay bill",
                        "reference_label": "pay_bill",
                    }
                ],
            )
            with patch("mississauga_unheard.intents._training_groups", return_value=training):
                result = evaluate_audio_intents(output, output)

            self.assertEqual(result[0]["correct"], "1")
            self.assertIn("audio transcript", result[0]["status"])
            predictions = (output / "audio_intent_predictions.csv").read_text(
                encoding="utf-8-sig"
            )
            self.assertIn("pay_bill", predictions)
            self.assertIn("true_label,predicted_label,count", (output / "audio_intent_confusions.csv").read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
