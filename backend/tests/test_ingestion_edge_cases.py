
from pathlib import Path
import tempfile

import pymupdf

from app.services.ingestion import (
    process_pdf,
    PDFIngestionError,
    UnsupportedScannedPDFError,
)


def create_pdf(path: Path, pages: list[str]) -> None:
    """Create a PDF containing the supplied page text."""
    with pymupdf.open() as pdf:
        for text in pages:
            page = pdf.new_page()
            if text:
                page.insert_text((72, 72), text)
        pdf.save(path)


with tempfile.TemporaryDirectory() as temp_dir:
    folder = Path(temp_dir)

    # 1. Missing PDF
    try:
        process_pdf(
            folder / "missing.pdf",
            document_id="doc1",
            workspace_id="workspace1",
            filename="missing.pdf",
        )
        raise AssertionError("Missing PDF should raise an error")
    except PDFIngestionError:
        print("PASS: Missing PDF is handled")

    # 2. Empty PDF
    empty_pdf = folder / "empty.pdf"
    create_pdf(empty_pdf, [""])

    try:
        process_pdf(
            empty_pdf,
            document_id="doc2",
            workspace_id="workspace1",
            filename="empty.pdf",
        )
        raise AssertionError("Empty PDF should raise an error")
    except UnsupportedScannedPDFError:
        print("PASS: Empty PDF is handled")

    # 3. Stable chunk IDs
    normal_pdf = folder / "normal.pdf"
    create_pdf(normal_pdf, ["TraceMind PDF ingestion test."])

    first_run = process_pdf(
        normal_pdf,
        document_id="doc3",
        workspace_id="workspace1",
        filename="normal.pdf",
    )
    second_run = process_pdf(
        normal_pdf,
        document_id="doc3",
        workspace_id="workspace1",
        filename="normal.pdf",
    )

    assert [c.chunk_id for c in first_run] == [
        c.chunk_id for c in second_run
    ]
    print("PASS: Chunk IDs are stable")

print("\nAll edge-case tests passed!")
