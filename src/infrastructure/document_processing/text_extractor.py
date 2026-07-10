import csv

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

    def extract_csv_rows(
        self,
        file_path: str,
    ) -> list[tuple[str, str, int]]:

        path = Path(file_path)

        with path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV file does not contain a header row."
                )

            normalized_columns = {
                column.strip().lower(): column
                for column in reader.fieldnames
            }

            required_columns = {
                "question",
                "answer",
            }

            missing_columns = (
                required_columns
                - set(normalized_columns)
            )

            if missing_columns:
                raise ValueError(
                    "CSV file must contain "
                    "'question' and 'answer' columns."
                )

            question_column = normalized_columns[
                "question"
            ]

            answer_column = normalized_columns[
                "answer"
            ]

            rows: list[
                tuple[str, str, int]
            ] = []

            for row_number, row in enumerate(
                reader,
                start=2,
            ):

                question = (
                    row.get(question_column)
                    or ""
                ).strip()

                answer = (
                    row.get(answer_column)
                    or ""
                ).strip()

                if not question and not answer:
                    continue

                if not question:
                    raise ValueError(
                        f"Question is empty at CSV "
                        f"row {row_number}."
                    )

                rows.append(
                    (
                        question,
                        answer,
                        row_number,
                    )
                )

        if not rows:
            raise ValueError(
                "CSV file does not contain any valid data."
            )

        return rows
