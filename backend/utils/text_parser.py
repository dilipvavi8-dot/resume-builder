from io import BytesIO
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return content.decode("utf-8", errors="ignore")
    if suffix == ".docx":
        document = Document(BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs if p.text.strip())
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError("Supported formats are DOCX, PDF, and TXT.")


def normalize_words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#.-]+", text.lower()))
