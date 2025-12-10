from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _run_cli(args: list[str]) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


class TestCLI(unittest.TestCase):
    def test_text_cli_inline_arguments(self) -> None:
        output = _run_cli(
            [
                "text",
                "--submission",
                "The quick brown fox repeats.",
                "--reference",
                "A fast brown fox jumps.",
                "--pretty",
            ]
        )

        self.assertTrue(output["submission"].startswith("The quick brown fox"))
        self.assertEqual(output["references"], ["A fast brown fox jumps."])
        self.assertGreaterEqual(output["max_similarity"], 0.0)
        self.assertLessEqual(output["max_similarity"], 1.0)
        self.assertGreaterEqual(output["repetition_score"], 0.0)

    def test_text_cli_file_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            submission_file = Path(tmpdir) / "submission.txt"
            reference_file = Path(tmpdir) / "reference.txt"
            submission_file.write_text("repeat repeat repeat", encoding="utf-8")
            reference_file.write_text("repeat", encoding="utf-8")

            output = _run_cli(
                [
                    "text",
                    "--submission-file",
                    str(submission_file),
                    "--reference-file",
                    str(reference_file),
                    "--repetition-ngram",
                    "1",
                    "--phrase-limit",
                    "-1",
                ]
            )

        self.assertEqual(output["submission"], "repeat repeat repeat")
        self.assertEqual(output["references"], ["repeat"])
        self.assertEqual(output["repetition_ngram_size"], 1)
        self.assertTrue(output["repeated_phrases"])
