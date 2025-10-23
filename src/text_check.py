"""Utility functions for text similarity and repetition analysis.

This module implements TF-IDF cosine similarity to detect overlap between
texts as well as a heuristic "AI repetition" score that estimates how
repetitive a piece of writing is.  The functions are designed for use
within the Streamlit application as well as simple script execution.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import re
from typing import List, Sequence, Tuple, TypedDict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    """Tokenise text into lowercase alphanumeric tokens."""
    return _WORD_RE.findall(text.lower())


def tfidf_cosine_similarity(
    text_a: str, text_b: str, *, ngram_range: tuple[int, int] = (1, 2)
) -> float:
    """Return the cosine similarity between two texts using TF-IDF vectors."""
    if not text_a.strip() or not text_b.strip():
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=ngram_range)
    tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(similarity_matrix[0, 0])


class RepeatedPhrase(TypedDict):
    phrase: str
    count: int
    share: float


def ai_repetition_details(
    text: str, *, ngram_size: int = 3, limit: int | None = 5
) -> Tuple[float, List[RepeatedPhrase]]:
    """Return repetition score and a breakdown of repeated n-grams.

    Parameters
    ----------
    text:
        Input string to analyse.
    ngram_size:
        Token length of n-grams considered for repetition detection.
    limit:
        Maximum number of repeated phrases to include in the breakdown.

    Returns
    -------
    Tuple containing the repetition score in the range [0, 1] and a list of
    repeated phrase dictionaries sorted by frequency.
    """

    tokens = _tokenize(text)
    if len(tokens) < ngram_size or not tokens:
        return 0.0, []

    ngrams = [tuple(tokens[i : i + ngram_size]) for i in range(len(tokens) - ngram_size + 1)]
    counts = Counter(ngrams)
    total = sum(counts.values())
    if total == 0:
        return 0.0, []

    repeated_items = [(ngram, count) for ngram, count in counts.items() if count > 1]
    repeated_items.sort(key=lambda item: (-item[1], item[0]))

    repeated_total = sum(count for _, count in repeated_items)
    score = float(min(max(repeated_total / total, 0.0), 1.0))

    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    if limit is None:
        selected_items = repeated_items
    elif limit == 0:
        selected_items = []
    else:
        selected_items = repeated_items[:limit]

    top_phrases: List[RepeatedPhrase] = []
    for ngram, count in selected_items:
        phrase = " ".join(ngram)
        share = count / total if total else 0.0
        top_phrases.append({"phrase": phrase, "count": int(count), "share": float(share)})

    return score, top_phrases


def ai_repetition_score(text: str, *, ngram_size: int = 3) -> float:
    """Return only the repetition score for backward compatibility."""

    score, _ = ai_repetition_details(text, ngram_size=ngram_size, limit=0)
    return score


@dataclass(slots=True)
class TextAnalysisResult:
    """Combined similarity and repetition metrics for a text submission."""

    submission: str
    references: Sequence[str]
    similarities: List[float]
    max_similarity: float
    mean_similarity: float
    repetition_score: float
    repeated_phrases: List[RepeatedPhrase]
    repetition_ngram_size: int
    vectorizer_ngram_range: Tuple[int, int]

    def to_dict(self) -> dict:
        return {
            "submission": self.submission,
            "references": list(self.references),
            "similarities": self.similarities,
            "max_similarity": self.max_similarity,
            "mean_similarity": self.mean_similarity,
            "repetition_score": self.repetition_score,
            "repeated_phrases": self.repeated_phrases,
            "repetition_ngram_size": self.repetition_ngram_size,
            "vectorizer_ngram_range": list(self.vectorizer_ngram_range),
        }


def analyse_submission(
    submission: str,
    references: Sequence[str],
    *,
    ngram_range: Tuple[int, int] = (1, 2),
    repetition_ngram_size: int = 3,
    repetition_phrase_limit: int | None = 5,
) -> TextAnalysisResult:
    """Analyse a text submission against reference texts.

    Parameters
    ----------
    submission:
        The text under inspection.
    references:
        A sequence of comparison texts.  Empty or whitespace-only entries
        are ignored.
    ngram_range:
        The n-gram configuration supplied to the TF-IDF vectoriser.
        Customising this allows for character-level matching when analysing
        languages without whitespace tokenisation.
    repetition_ngram_size:
        Token span used to compute the repetition score.
    repetition_phrase_limit:
        Maximum number of repeated phrases returned in the result.  Use
        ``None`` to return all repeated phrases.
    """

    cleaned_references = [ref for ref in references if ref and ref.strip()]
    if not cleaned_references:
        raise ValueError("At least one non-empty reference text is required.")

    similarities = [
        tfidf_cosine_similarity(submission, reference, ngram_range=ngram_range)
        for reference in cleaned_references
    ]
    max_similarity = max(similarities)
    mean_similarity = sum(similarities) / len(similarities)
    repetition, repeated_phrases = ai_repetition_details(
        submission, ngram_size=repetition_ngram_size, limit=repetition_phrase_limit
    )

    return TextAnalysisResult(
        submission=submission,
        references=cleaned_references,
        similarities=similarities,
        max_similarity=max_similarity,
        mean_similarity=mean_similarity,
        repetition_score=repetition,
        repeated_phrases=repeated_phrases,
        repetition_ngram_size=repetition_ngram_size,
        vectorizer_ngram_range=ngram_range,
    )


def _demo() -> None:
    """Simple demonstration executed when running this module as a script."""

    submission = "The quick brown fox jumps over the lazy dog. The quick brown fox repeats."
    references = [
        "A fast brown fox leaps across a sleepy canine.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    ]
    result = analyse_submission(submission, references)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
