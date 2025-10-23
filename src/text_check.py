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
from typing import List, Sequence

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


def ai_repetition_score(text: str, *, ngram_size: int = 3) -> float:
    """Estimate repetition by measuring repeated n-gram frequency.

    The score ranges from 0.0 to 1.0 and represents the proportion of
    repeated n-grams in the text.  A higher value indicates more repetition,
    which can be symptomatic of low-quality or AI-generated content.
    """

    tokens = _tokenize(text)
    if len(tokens) < ngram_size or not tokens:
        return 0.0

    ngrams = [tuple(tokens[i : i + ngram_size]) for i in range(len(tokens) - ngram_size + 1)]
    counts = Counter(ngrams)
    total = sum(counts.values())
    if total == 0:
        return 0.0

    repeated = sum(count for count in counts.values() if count > 1)
    score = repeated / total
    return float(min(max(score, 0.0), 1.0))


@dataclass(slots=True)
class TextAnalysisResult:
    """Combined similarity and repetition metrics for a text submission."""

    submission: str
    references: Sequence[str]
    similarities: List[float]
    max_similarity: float
    mean_similarity: float
    repetition_score: float

    def to_dict(self) -> dict:
        return {
            "submission": self.submission,
            "references": list(self.references),
            "similarities": self.similarities,
            "max_similarity": self.max_similarity,
            "mean_similarity": self.mean_similarity,
            "repetition_score": self.repetition_score,
        }


def analyse_submission(submission: str, references: Sequence[str]) -> TextAnalysisResult:
    """Analyse a text submission against reference texts.

    Parameters
    ----------
    submission:
        The text under inspection.
    references:
        A sequence of comparison texts.  Empty or whitespace-only entries
        are ignored.
    """

    cleaned_references = [ref for ref in references if ref and ref.strip()]
    if not cleaned_references:
        raise ValueError("At least one non-empty reference text is required.")

    similarities = [
        tfidf_cosine_similarity(submission, reference) for reference in cleaned_references
    ]
    max_similarity = max(similarities)
    mean_similarity = sum(similarities) / len(similarities)
    repetition = ai_repetition_score(submission)

    return TextAnalysisResult(
        submission=submission,
        references=cleaned_references,
        similarities=similarities,
        max_similarity=max_similarity,
        mean_similarity=mean_similarity,
        repetition_score=repetition,
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
