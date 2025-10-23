import unittest

from PIL import Image

from src import image_check


class ImageCheckTests(unittest.TestCase):
    def test_identical_images_have_full_similarity(self) -> None:
        image = Image.new("RGB", (32, 32), color="white")
        similarity = image_check.image_similarity(image, image)
        self.assertAlmostEqual(similarity, 1.0, places=7)

    def test_different_images_reduce_similarity(self) -> None:
        image_a = Image.new("RGB", (32, 32), color="black")
        image_b = Image.new("RGB", (32, 32), color="white")

        hash_a = image_check.phash(image_a)
        hash_b = image_check.phash(image_b)

        similarity = image_check.hash_similarity(hash_a, hash_b)
        self.assertLess(similarity, 1.0)
        self.assertGreaterEqual(similarity, 0.0)

        distance = image_check.hash_distance(hash_a, hash_b)
        total_bits = len(image_check.hash_to_bits(hash_a))
        self.assertLessEqual(distance, total_bits)


if __name__ == "__main__":
    unittest.main()
