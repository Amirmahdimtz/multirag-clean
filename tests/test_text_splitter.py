import unittest

from src.infrastructure.document_processing.text_splitter import TextSplitter


class TextSplitterTests(unittest.TestCase):
    def test_empty_text_returns_no_chunks(self) -> None:
        splitter = TextSplitter(chunk_size=10, chunk_overlap=2)

        self.assertEqual([], splitter.split("  \n\n  "))

    def test_normalizes_blank_lines_and_surrounding_whitespace(self) -> None:
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)

        chunks = splitter.split("  alpha  \n\n  beta  ")

        self.assertEqual(["alpha\nbeta"], chunks)

    def test_applies_configured_overlap(self) -> None:
        splitter = TextSplitter(chunk_size=6, chunk_overlap=2)

        chunks = splitter.split("abcdefghij")

        self.assertEqual(["abcdef", "efghij", "ij"], chunks)

    def test_overlap_must_be_smaller_than_chunk_size(self) -> None:
        with self.assertRaises(ValueError):
            TextSplitter(chunk_size=10, chunk_overlap=10)


if __name__ == "__main__":
    unittest.main()
