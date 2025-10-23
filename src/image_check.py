"""Perceptual hash image similarity utilities."""

from __future__ import annotations

import json

import numpy as np
from PIL import Image
from scipy.fftpack import dct


def phash(image: Image.Image, *, hash_size: int = 8, highfreq_factor: int = 4) -> np.ndarray:
    """Return the perceptual hash of an image using the discrete cosine transform."""

    if hash_size <= 0:
        raise ValueError("hash_size must be positive")
    if highfreq_factor <= 0:
        raise ValueError("highfreq_factor must be positive")

    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), Image.LANCZOS)
    pixels = np.asarray(image, dtype=float)

    dct_rows = dct(pixels, axis=0, norm="ortho")
    dct_values = dct(dct_rows, axis=1, norm="ortho")
    low_freq = dct_values[:hash_size, :hash_size]

    # Exclude the DC component when computing the median.
    median = np.median(low_freq[1:, 1:]) if hash_size > 1 else np.median(low_freq)
    return (low_freq > median).astype(np.uint8)


def hash_distance(hash_a: np.ndarray, hash_b: np.ndarray) -> int:
    """Return the Hamming distance between two perceptual hashes."""

    if hash_a.shape != hash_b.shape:
        raise ValueError("Hash shapes must match for comparison")
    return int(np.count_nonzero(hash_a != hash_b))


def hash_similarity(hash_a: np.ndarray, hash_b: np.ndarray) -> float:
    """Return a normalised similarity score between 0 and 1 for two hashes."""

    distance = hash_distance(hash_a, hash_b)
    total_bits = hash_a.size
    return 1.0 - (distance / total_bits)


def image_similarity(
    image_a: Image.Image, image_b: Image.Image, *, hash_size: int = 8, highfreq_factor: int = 4
) -> float:
    """Compute pHash similarity between two images."""

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
        "hash1": phash(img1).flatten().tolist(),
        "hash2": phash(img2).flatten().tolist(),
    }
    print(json.dumps(demo, indent=2))


if __name__ == "__main__":
    _demo()
