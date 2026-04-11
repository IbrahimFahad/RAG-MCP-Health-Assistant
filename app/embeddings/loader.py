import fitz  # PyMuPDF
import os
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Document:
    """Represents a loaded document before chunking."""
    text: str
    source: str          # file path or URL
    title: str = ""
    language: str = ""   # 'ar', 'en', or '' if unknown
    metadata: dict = field(default_factory=dict)


def load_pdf(file_path: str) -> Document:
    """
    Extract text from a PDF file using PyMuPDF.
    Handles Arabic (RTL) and English text correctly.
    Pages are joined with double newlines.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    doc = fitz.open(file_path)
    pages_text = []

    for page_num, page in enumerate(doc):
        # 'text' mode preserves reading order, handles RTL Arabic
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text.strip())

    doc.close()
    full_text = "\n\n".join(pages_text)

    return Document(
        text=full_text,
        source=str(path),
        title=path.stem,
        metadata={"file_type": "pdf", "pages": len(pages_text)}
    )


def load_text(file_path: str) -> Document:
    """
    Load a plain .txt file.
    Tries UTF-8 first, then falls back to common Arabic encodings.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    for encoding in ["utf-8", "utf-8-sig", "windows-1256", "iso-8859-6"]:
        try:
            text = path.read_text(encoding=encoding)
            return Document(
                text=text.strip(),
                source=str(path),
                title=path.stem,
                metadata={"file_type": "txt", "encoding": encoding}
            )
        except (UnicodeDecodeError, LookupError):
            continue

    raise ValueError(f"Could not decode file with any known encoding: {file_path}")


def load_document(file_path: str) -> Document:
    """
    Auto-detect file type and load accordingly.
    Supports: .pdf, .txt
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".txt":
        return load_text(file_path)
    else:
        raise ValueError(f"Unsupported file type '{ext}'. Supported: .pdf, .txt")


def load_from_string(text: str, title: str = "manual", source: str = "manual") -> Document:
    """Create a Document directly from a string (useful for testing or web-scraped content)."""
    return Document(
        text=text.strip(),
        source=source,
        title=title,
        metadata={"file_type": "string"}
    )
