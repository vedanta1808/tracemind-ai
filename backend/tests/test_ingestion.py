
from pathlib import Path

import pymupdf

from app.services.ingestion import process_pdf


# Create a sample PDF with two pages.
pdf_path = Path("sample_test.pdf")

with pymupdf.open() as pdf:
    page1 = pdf.new_page()
    page1.insert_text((72, 72), "This is the first page of TraceMind.")

    page2 = pdf.new_page()
    page2.insert_text((72, 72), "This is the second page of TraceMind.")

    pdf.save(pdf_path)

# Process the sample PDF.
chunks = process_pdf(
    pdf_path,
    document_id="test-document-001",
    workspace_id="test-workspace-001",
    filename="sample_test.pdf",
)

# Display the results.
print(f"\nTotal chunks created: {len(chunks)}")

for chunk in chunks:
    print("\n------------------------------")
    print(f"Chunk ID: {chunk.chunk_id}")
    print(f"Document ID: {chunk.document_id}")
    print(f"Filename: {chunk.filename}")
    print(f"Page number: {chunk.page_number}")
    print(f"Text: {chunk.text}")

# Verify the expected output.
assert len(chunks) == 2, "Expected two chunks."
assert chunks[0].page_number == 1, "First chunk should reference page 1."
assert chunks[1].page_number == 2, "Second chunk should reference page 2."

print("\nSUCCESS: PDF ingestion test passed!")
