"""Perceptual hash image similarity utilities."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable as IterableABC
from typing import Iterable, List, Sequence

try:  # NumPy is optional for constrained execution environments
    import numpy as np
except Exception:  # pragma: no cover - used when numpy is unavailable
    np = None  # type: ignore[assignment]

try:  # SciPy is optional for constrained execution environments
    from scipy.fftpack import dct as scipy_dct
except Exception:  # pragma: no cover - used when scipy is unavailable
    scipy_dct = None  # type: ignore[assignment]

from PIL import Image


def _ortho_dct_1d(vector: Sequence[float]) -> List[float]:
    """Fallback implementation of an orthonormal DCT-II transform."""
    n = len(vector)
    if n == 0:
        return []
    result: List[float] = []
    factor = math.pi / n
    scale0 = math.sqrt(1 / n)
    scale = math.sqrt(2 / n)
    for k in range(n):
        coeff = scale0 if k == 0 else scale
        total = 0.0
        for i, value in enumerate(vector):
            total += value * math.cos((i + 0.5) * k * factor)
        result.append(coeff * total)
    return result


def _ortho_dct_2d(matrix: Sequence[Sequence[float]]) -> List[List[float]]:
    """Compute a 2D orthonormal DCT using separability."""
    if scipy_dct is not None and np is not None:
        arr = np.asarray(matrix, dtype=float)
        dct_rows = scipy_dct(arr, axis=0, norm="ortho")
        dct_values = scipy_dct(dct_rows, axis=1, norm="ortho")
        return dct_values.tolist()

    temp = [_ortho_dct_1d(row) for row in matrix]
    # Transpose
    transposed = list(map(list, zip(*temp))) if temp else []
    dct_cols = [_ortho_dct_1d(col) for col in transposed]
    # Transpose back
    return [list(row) for row in zip(*dct_cols)] if dct_cols else []


def _grayscale_pixels(image: Image.Image, size: int) -> List[List[float]]:
    gray = image.convert("L").resize((size, size), Image.LANCZOS)
    pixels = list(gray.getdata())
    return [pixels[i * size : (i + 1) * size] for i in range(size)]


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2:
        return float(sorted_vals[mid])
    return float((sorted_vals[mid - 1] + sorted_vals[mid]) / 2)


def _binary_matrix(matrix: Sequence[Sequence[float]], threshold: float):
    if np is not None:
        arr = np.asarray(matrix, dtype=float)
        return (arr > threshold).astype(np.uint8)
    return [[1 if value > threshold else 0 for value in row] for row in matrix]


def _flatten_hash(hash_value: Iterable[Iterable[int]] | "np.ndarray") -> List[int]:
    if np is not None and isinstance(hash_value, np.ndarray):
        return hash_value.astype(int).ravel().tolist()
    flattened: List[int] = []
    for row in hash_value:  # type: ignore[iteration-over-optional]
        if isinstance(row, IterableABC) and not isinstance(row, (int, bool)):
            flattened.extend(int(col) for col in row)  # type: ignore[arg-type]
        else:
            flattened.append(int(row))  # type: ignore[arg-type]
    return flattened


def hash_to_bits(hash_value: Iterable[Iterable[int]] | "np.ndarray") -> List[int]:
    """Return the flattened perceptual hash as a list of integers."""
    return _flatten_hash(hash_value)


def phash(
    image: Image.Image, *, hash_size: int = 8, highfreq_factor: int = 4
) -> "np.ndarray | List[List[int]]":
    """Return the perceptual hash of an image using the discrete cosine transform.

    Parameters
    ----------
    image:
        The PIL Image to hash.
    hash_size:
        The dimension of the resulting hash (default 8x8 = 64 bits).
    highfreq_factor:
        Factor to determine the image size for DCT computation.

    Returns
    -------
    A numpy array or list of lists representing the binary hash.
    """
    if hash_size <= 0:
        raise ValueError("hash_size must be positive")
    if highfreq_factor <= 0:
        raise ValueError("highfreq_factor must be positive")

    img_size = hash_size * highfreq_factor
    pixels = _grayscale_pixels(image, img_size)
    dct_values = _ortho_dct_2d(pixels)
    low_freq = [row[:hash_size] for row in dct_values[:hash_size]]

    if hash_size > 1:
        region = [value for i, row in enumerate(low_freq) for j, value in enumerate(row) if i or j]
    else:
        region = [value for row in low_freq for value in row]

    if np is not None:
        median = float(np.median(region)) if region else 0.0
    else:
        median = _median(region)
    return _binary_matrix(low_freq, median)


def hash_distance(
    hash_a: "np.ndarray | Iterable[Iterable[int]]",
    hash_b: "np.ndarray | Iterable[Iterable[int]]",
) -> int:
    """Return the Hamming distance between two perceptual hashes.

    Parameters
    ----------
    hash_a:
        First hash to compare.
    hash_b:
        Second hash to compare.

    Returns
    -------
    The Hamming distance (number of differing bits).
    """
    flat_a = _flatten_hash(hash_a)
    flat_b = _flatten_hash(hash_b)
    if len(flat_a) != len(flat_b):
        raise ValueError("Hash shapes must match for comparison")
    return sum(1 for a, b in zip(flat_a, flat_b) if a != b)


def hash_similarity(
    hash_a: "np.ndarray | Iterable[Iterable[int]]",
    hash_b: "np.ndarray | Iterable[Iterable[int]]",
) -> float:
    """Return a normalised similarity score between 0 and 1 for two hashes.

    Parameters
    ----------
    hash_a:
        First hash to compare.
    hash_b:
        Second hash to compare.

    Returns
    -------
    Similarity score where 1.0 means identical and 0.0 means completely different.
    """
    distance = hash_distance(hash_a, hash_b)
    total_bits = len(_flatten_hash(hash_a))
    return 1.0 - (distance / total_bits) if total_bits else 0.0


def image_similarity(
    image_a: Image.Image,
    image_b: Image.Image,
    *,
    hash_size: int = 8,
    highfreq_factor: int = 4,
) -> float:
    """Compute pHash similarity between two images.

    Parameters
    ----------
    image_a:
        First image to compare.
    image_b:
        Second image to compare.
    hash_size:
        The dimension of the perceptual hash (default 8x8 = 64 bits).
    highfreq_factor:
        Factor to determine the image size for DCT computation.

    Returns
    -------
    Similarity score between 0.0 and 1.0.
    """
    hash_a = phash(image_a, hash_size=hash_size, highfreq_factor=highfreq_factor)
    hash_b = phash(image_b, hash_size=hash_size, highfreq_factor=highfreq_factor)
    return hash_similarity(hash_a, hash_b)


def _demo() -> None:
    """Simple smoke test comparing two generated images."""
    img1 = Image.new("RGB", (64, 64), color="navy")
    img2 = Image.new("RGB", (64, 64), color="blue")
    similarity = image_similarity(img1, img2)
    demo = {
        "similarity": similarity,
        "hash1": hash_to_bits(phash(img1)),
        "hash2": hash_to_bits(phash(img2)),
    }
    print(json.dumps(demo, indent=2))


if __name__ == "__main__":
    _demo()
