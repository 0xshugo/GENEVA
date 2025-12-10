import unittest

from src import text_check


class TextCheckTests(unittest.TestCase):
    def test_similarity_identical_and_distinct(self) -> None:
        identical = text_check.tfidf_cosine_similarity("GENEVA", "GENEVA")
        self.assertAlmostEqual(identical, 1.0, places=7)

        different = text_check.tfidf_cosine_similarity("ethics", "robotics")
        self.assertGreaterEqual(different, 0.0)
        self.assertLessEqual(different, 0.5)

    def test_analyse_submission_reports_repetition(self) -> None:
        submission = "The quick brown fox jumps over the lazy dog. The quick brown fox repeats."
        references = [
            "A fast brown fox leaps across a sleepy canine.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        ]

        analysis = text_check.analyse_submission(submission, references)

        self.assertEqual(len(analysis.similarities), len(references))
        self.assertGreater(analysis.max_similarity, 0.0)
        self.assertGreaterEqual(analysis.mean_similarity, 0.0)
        self.assertGreaterEqual(analysis.repetition_score, 0.0)
        self.assertLessEqual(analysis.repetition_score, 1.0)
        self.assertTrue(any(
            phrase["phrase"] == "quick brown fox" for phrase in analysis.repeated_phrases
        ))

        serialised = analysis.to_dict()
        self.assertIn("similarities", serialised)
        self.assertIn("repeated_phrases", serialised)

    def test_empty_text_handling(self) -> None:
        """Test handling of empty strings."""
        empty_similarity = text_check.tfidf_cosine_similarity("", "some text")
        self.assertEqual(empty_similarity, 0.0)

        empty_both = text_check.tfidf_cosine_similarity("", "")
        self.assertEqual(empty_both, 0.0)

        # Repetition score should be 0 for empty text
        empty_score = text_check.ai_repetition_score("")
        self.assertEqual(empty_score, 0.0)

    def test_whitespace_only_text(self) -> None:
        """Test handling of whitespace-only strings."""
        whitespace_similarity = text_check.tfidf_cosine_similarity("   ", "test")
        self.assertEqual(whitespace_similarity, 0.0)

    def test_non_ascii_characters(self) -> None:
        """Test handling of Japanese and emoji characters."""
        japanese_text1 = "これはテストです"
        japanese_text2 = "これはテストです"

        similarity = text_check.tfidf_cosine_similarity(japanese_text1, japanese_text2)
        self.assertAlmostEqual(similarity, 1.0, places=7)

        # Test with emojis
        emoji_text = "Hello 😊 World 😊"
        score = text_check.ai_repetition_score(emoji_text)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_repetition_details_limit(self) -> None:
        """Test repetition_phrase_limit parameter."""
        # Create text with clear repetition (use longer repeated sequences)
        text = "the quick brown fox the quick brown fox jumps over the lazy dog"

        # Test with limit
        score, phrases = text_check.ai_repetition_details(text, ngram_size=3, limit=1)
        self.assertLessEqual(len(phrases), 1)

        # Test with limit=0
        score, phrases = text_check.ai_repetition_details(text, limit=0)
        self.assertEqual(len(phrases), 0)

        # Test with limit=None (all phrases)
        score, phrases = text_check.ai_repetition_details(text, ngram_size=2, limit=None)
        self.assertGreater(len(phrases), 0)

    def test_analyse_submission_error_handling(self) -> None:
        """Test error handling for invalid inputs."""
        with self.assertRaises(ValueError):
            # Empty references should raise ValueError
            text_check.analyse_submission("test", [])

        with self.assertRaises(ValueError):
            # All whitespace references should raise ValueError
            text_check.analyse_submission("test", ["   ", "  "])


if __name__ == "__main__":
    unittest.main()
