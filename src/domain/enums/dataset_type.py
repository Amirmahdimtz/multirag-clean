from enum import Enum


class DatasetType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    CSV = "csv"
    UNKNOWN = "unknown"
