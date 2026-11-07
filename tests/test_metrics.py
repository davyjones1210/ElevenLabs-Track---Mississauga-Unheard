import unittest

from mississauga_unheard.metrics import character_error_rate, normalize_text, word_error_rate


class MetricsTests(unittest.TestCase):
    def test_normalizes_case_punctuation_and_unicode(self):
        self.assertEqual(normalize_text("HELLO,  café!"), "hello café")

    def test_word_error_rate(self):
        self.assertAlmostEqual(word_error_rate("turn on lights", "turn lights"), 1 / 3)

    def test_character_error_rate_ignores_spaces(self):
        self.assertAlmostEqual(character_error_rate("你好 世界", "你好界"), 1 / 4)

    def test_empty_reference(self):
        self.assertEqual(word_error_rate("", ""), 0)
        self.assertEqual(word_error_rate("", "hello"), 1)


if __name__ == "__main__":
    unittest.main()
