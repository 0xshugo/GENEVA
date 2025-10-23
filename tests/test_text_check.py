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


if __name__ == "__main__":
    unittest.main()
