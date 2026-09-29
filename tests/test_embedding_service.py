import math
import unittest

from src.infrastructure.embedding.embedding_service import EmbeddingService


class EmbeddingServiceTests(unittest.TestCase):
    def test_embedding_is_deterministic(self) -> None:
        service = EmbeddingService(dimension=32)

        first = service.embed_text("retrieval augmented generation")
        second = service.embed_text("retrieval augmented generation")

        self.assertEqual(first, second)

    def test_non_empty_embedding_is_unit_normalized(self) -> None:
        service = EmbeddingService(dimension=32)

        embedding = service.embed_text("vector search")

        norm = math.sqrt(sum(value * value for value in embedding))
        self.assertAlmostEqual(1.0, norm)

    def test_empty_text_returns_zero_vector(self) -> None:
        service = EmbeddingService(dimension=8)

        embedding = service.embed_text("   ")

        self.assertEqual([0.0] * 8, embedding)


if __name__ == "__main__":
    unittest.main()
