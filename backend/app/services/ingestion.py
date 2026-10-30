
"""PDF ingestion and text extraction for TraceMind."""

import hashlib
from datetime import date
from pathlib import Path

import pymupdf

from app.schemas import DocumentChunk
from app.services.chunking import chunk_text


class PDFIngestionError(Exception):
    """Raised when a PDF cannot be processed."""


class UnsupportedScannedPDFError(PDFIngestionError):
    """Raised when a PDF has no extractable text."""


def process_pdf(
    path: str | Path,
    *,
    document_id: str,
    workspace_id: str,
    filename: str,
    source_date: date | None = None,
    version_group: str | None = None,
) -> list[DocumentChunk]:
    """
    Extract text from a PDF page by page and split it into chunks.

    Each chunk retains its source page number and document metadata.

    Args:
        path: Path to the source PDF.
        document_id: Unique identifier for the document version.
        workspace_id: Workspace containing the document.
        filename: Original PDF filename.
        source_date: Optional date associated with the source.
        version_group: Optional identifier grouping document versions.

    Returns:
        A list of DocumentChunk objects.

    Raises:
        PDFIngestionError: If the PDF is missing, invalid, or unreadable.
        UnsupportedScannedPDFError: If the PDF contains no extractable text.
    """
    pdf_path = Path(path)

    if not pdf_path.is_file():
        raise PDFIngestionError(f"PDF file not found: {pdf_path}")

    chunks: list[DocumentChunk] = []
    extracted_text_found = False

    try:
        with pymupdf.open(pdf_path) as pdf:
            if pdf.is_encrypted:
                raise PDFIngestionError(
                    f"The PDF is encrypted and cannot be processed: {filename}"
                )

            for page_index, page in enumerate(pdf):
                page_number = page_index + 1
                page_text = page.get_text("text").strip()

                if not page_text:
                    continue

                extracted_text_found = True
                page_chunks = chunk_text(page_text)

                for chunk_index, text in enumerate(page_chunks):
                    # Stable for the same document version, page and chunk.
                    identifier_input = (
                        f"{document_id}:{page_number}:{chunk_index}:{text}"
                    )
                    chunk_id = hashlib.sha256(
                        identifier_input.encode("utf-8")
                    ).hexdigest()

                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            filename=filename,
                            page_number=page_number,
                            text=text,
                        )
                    )

    except PDFIngestionError:
        raise
    except Exception as exc:
        raise PDFIngestionError(
            f"Could not read PDF '{filename}': {exc}"
        ) from exc

    if not extracted_text_found:
        raise UnsupportedScannedPDFError(
            f"No extractable text was found in '{filename}'. "
            "The PDF may be scanned or empty; OCR is not supported."
        )

    return chunks
