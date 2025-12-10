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

    def test_hash_to_bits_conversion(self) -> None:
        """Test hash to bits conversion."""
        image = Image.new("RGB", (16, 16), color="blue")
        hash_value = image_check.phash(image)
        bits = image_check.hash_to_bits(hash_value)

        # Default hash_size is 8, so we should have 64 bits
        self.assertEqual(len(bits), 64)
        # All values should be 0 or 1
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_different_image_sizes(self) -> None:
        """Test that images of different sizes can be compared."""
        small_image = Image.new("RGB", (16, 16), color="red")
        large_image = Image.new("RGB", (128, 128), color="red")

        similarity = image_check.image_similarity(small_image, large_image)
        # Similar color should produce high similarity
        self.assertGreater(similarity, 0.5)

    def test_different_image_modes(self) -> None:
        """Test images with different modes (RGB, RGBA, L)."""
        rgb_image = Image.new("RGB", (32, 32), color="green")
        rgba_image = Image.new("RGBA", (32, 32), color="green")
        gray_image = Image.new("L", (32, 32), color=128)

        # Should be able to compare different modes
        similarity_rgb_rgba = image_check.image_similarity(rgb_image, rgba_image)
        self.assertGreaterEqual(similarity_rgb_rgba, 0.0)
        self.assertLessEqual(similarity_rgb_rgba, 1.0)

        similarity_rgb_gray = image_check.image_similarity(rgb_image, gray_image)
        self.assertGreaterEqual(similarity_rgb_gray, 0.0)
        self.assertLessEqual(similarity_rgb_gray, 1.0)

    def test_phash_parameter_validation(self) -> None:
        """Test parameter validation in phash function."""
        image = Image.new("RGB", (32, 32), color="white")

        # Invalid hash_size
        with self.assertRaises(ValueError):
            image_check.phash(image, hash_size=0)

        with self.assertRaises(ValueError):
            image_check.phash(image, hash_size=-1)

        # Invalid highfreq_factor
        with self.assertRaises(ValueError):
            image_check.phash(image, highfreq_factor=0)

    def test_hash_distance_mismatched_sizes(self) -> None:
        """Test that hash_distance raises error for mismatched hash sizes."""
        image = Image.new("RGB", (32, 32), color="white")

        hash_8 = image_check.phash(image, hash_size=8)
        hash_16 = image_check.phash(image, hash_size=16)

        with self.assertRaises(ValueError):
            image_check.hash_distance(hash_8, hash_16)


if __name__ == "__main__":
    unittest.main()
