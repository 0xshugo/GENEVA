"""Regression tests ensuring the repository is free from merge conflict markers."""

from __future__ import annotations

import subprocess
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFLICT_MARKERS = (
    "<" * 7,
    "=" * 7,
    ">" * 7,
    "|" * 7,
)


def _tracked_text_files() -> list[Path]:
    """Return tracked repository files that can be decoded as text."""

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    tracked_paths: list[Path] = []
    for relative in result.stdout.splitlines():
        path = REPO_ROOT / relative
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary or non-UTF-8 files such as images.
            continue
        tracked_paths.append(path)
    return tracked_paths


class NoMergeConflictsTest(unittest.TestCase):
    def test_repository_has_no_conflict_markers(self) -> None:
        offending: list[Path] = []
        for path in _tracked_text_files():
            content = path.read_text(encoding="utf-8")
            if any(marker in content for marker in CONFLICT_MARKERS):
                offending.append(path)

        self.assertEqual(
            offending,
            [],
            msg="Merge conflict markers remain in: " + ", ".join(map(str, offending)),
        )


if __name__ == "__main__":
    unittest.main()
