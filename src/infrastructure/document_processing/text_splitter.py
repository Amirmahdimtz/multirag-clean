from typing import List


class TextSplitter:
    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        normalized_text = self.__normalize_text(text)

        if not normalized_text:
            return []

        chunks: list[str] = []
        start = 0
        text_length = len(normalized_text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = normalized_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def __normalize_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        non_empty_lines = [line for line in lines if line]
        return "\n".join(non_empty_lines)
