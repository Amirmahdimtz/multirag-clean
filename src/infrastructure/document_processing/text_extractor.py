from pathlib import Path

from docx import Document
from pypdf import PdfReader


class TextExtractor:
    def extract(self, file_path: str) -> str:
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".txt":
            return self.__extract_from_txt(path)

        if extension == ".pdf":
            return self.__extract_from_pdf(path)

        if extension == ".docx":
            return self.__extract_from_docx(path)

        raise ValueError(f"Unsupported file type: {extension}")

    def __extract_from_txt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def __extract_from_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages_text: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        return "\n".join(pages_text)

    def __extract_from_docx(self, path: Path) -> str:
        document = Document(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs)
