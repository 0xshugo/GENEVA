"""Regression tests ensuring the repository is free from merge conflict markers."""

from __future__ import annotations

import subprocess
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
_MARKER_CHARS = "<=>|"
_MARKER_WIDTH = 7


def _conflict_markers() -> tuple[str, ...]:
    """Return the canonical merge-conflict marker strings."""

    return tuple(char * _MARKER_WIDTH for char in _MARKER_CHARS)


CONFLICT_MARKERS = _conflict_markers()


def _unmerged_paths() -> list[Path]:
    """Return repository paths that are still staged as unmerged."""

    result = subprocess.run(
        ["git", "ls-files", "-u"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    paths: set[Path] = set()
    for line in result.stdout.splitlines():
        try:
            _metadata, path = line.split("\t", 1)
        except ValueError:
            continue
        paths.add((REPO_ROOT / path).resolve())
    return sorted(paths)


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
        unmerged = _unmerged_paths()
        unmerged_relative = [path.relative_to(REPO_ROOT) for path in unmerged]
        self.assertEqual(
            unmerged_relative,
            [],
            msg="Unmerged paths remain: " + ", ".join(map(str, unmerged_relative)),
        )

        offending: list[Path] = []
        for path in _tracked_text_files():
            content = path.read_text(encoding="utf-8")
            if any(marker in content for marker in CONFLICT_MARKERS):
                offending.append(path)

        offending_relative = [path.relative_to(REPO_ROOT) for path in offending]
        self.assertEqual(
            offending_relative,
            [],
            msg="Merge conflict markers remain in: "
            + ", ".join(map(str, offending_relative)),
        )


if __name__ == "__main__":
    unittest.main()
