"""Command-line interface for the GENEVA toolkit.

This module provides lightweight wrappers around the text and image
analysis utilities so they can be invoked from the terminal.  The text
subcommand mirrors the behaviour of the Streamlit UI by computing TF-IDF
cosine similarity against one or more references and returning the AI
repetition score breakdown.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image

from . import image_check, text_check


def _read_text_sources(text: str | None, files: Sequence[str]) -> str:
    """Combine inline text and file-based sources into a single string."""

    parts: list[str] = []
    if text:
        parts.append(text)
    for file_path in files:
        parts.append(Path(file_path).read_text(encoding="utf-8"))
    combined = "\n\n".join(part.strip() for part in parts if part and part.strip())
    if not combined:
        raise ValueError("A submission text is required (inline or file-based).")
    return combined


def _read_reference_sources(texts: Iterable[str], files: Sequence[str]) -> list[str]:
    references: list[str] = [item.strip() for item in texts if item and item.strip()]
    for file_path in files:
        content = Path(file_path).read_text(encoding="utf-8").strip()
        if content:
            references.append(content)
    if not references:
        raise ValueError("At least one reference text is required.")
    return references


def _text_subcommand(args: argparse.Namespace) -> dict:
    submission = _read_text_sources(args.submission, args.submission_file)
    references = _read_reference_sources(args.reference, args.reference_file)

    analysis = text_check.analyse_submission(
        submission,
        references,
        ngram_range=(args.ngram_min, args.ngram_max),
        repetition_ngram_size=args.repetition_ngram,
        repetition_phrase_limit=args.phrase_limit,
    )
    return analysis.to_dict()


def _image_subcommand(args: argparse.Namespace) -> dict:
    image_a = Image.open(args.image_a)
    image_b = Image.open(args.image_b)

    hash_a = image_check.phash(image_a, hash_size=args.hash_size, highfreq_factor=args.highfreq_factor)
    hash_b = image_check.phash(image_b, hash_size=args.hash_size, highfreq_factor=args.highfreq_factor)
    similarity = image_check.hash_similarity(hash_a, hash_b)
    return {
        "similarity": similarity,
        "hash_a": image_check.hash_to_bits(hash_a),
        "hash_b": image_check.hash_to_bits(hash_b),
        "hash_size": args.hash_size,
        "highfreq_factor": args.highfreq_factor,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GENEVA – Generative Ethics Validator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    text_parser = subparsers.add_parser("text", help="Analyse text similarity and repetition")
    text_parser.add_argument("--submission", help="Submission text to analyse", default=None)
    text_parser.add_argument(
        "--submission-file",
        action="append",
        default=[],
        help="Path to a file containing submission text (can be repeated)",
    )
    text_parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference text to compare against (can be repeated)",
    )
    text_parser.add_argument(
        "--reference-file",
        action="append",
        default=[],
        help="Path to a reference text file (can be repeated)",
    )
    text_parser.add_argument("--ngram-min", type=int, default=1, help="Minimum n-gram size for TF-IDF")
    text_parser.add_argument("--ngram-max", type=int, default=2, help="Maximum n-gram size for TF-IDF")
    text_parser.add_argument(
        "--repetition-ngram",
        type=int,
        default=3,
        help="n-gram size used to calculate the repetition score",
    )
    text_parser.add_argument(
        "--phrase-limit",
        type=int,
        default=5,
        help="Number of repeated phrases to include (use -1 for all)",
    )
    text_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON with indentation",
    )
    text_parser.set_defaults(func=_text_subcommand)

    image_parser = subparsers.add_parser("image", help="Compute pHash similarity between two images")
    image_parser.add_argument("--image-a", required=True, help="Path to the first image")
    image_parser.add_argument("--image-b", required=True, help="Path to the second image")
    image_parser.add_argument("--hash-size", type=int, default=8, help="Hash dimension (e.g., 8 for 8x8)")
    image_parser.add_argument(
        "--highfreq-factor",
        type=int,
        default=4,
        help="Scaling factor applied before computing the DCT",
    )
    image_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON with indentation")
    image_parser.set_defaults(func=_image_subcommand)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if getattr(args, "phrase_limit", None) == -1:
            args.phrase_limit = None
        result = args.func(args)
    except Exception as err:  # pragma: no cover - integration behaviour
        parser.error(str(err))
        return 2

    json_kwargs = {"ensure_ascii": False}
    if args.pretty:
        json_kwargs.update({"indent": 2})
    print(json.dumps(result, **json_kwargs))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution path
    raise SystemExit(main())
