
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from app.services.chunking import chunk_text

app = FastAPI(
    title="TraceMind API",
    description="AI-powered Personal Second Brain",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": "TraceMind"}


@app.post("/api/v1/documents/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    contents = await file.read(MAX_FILE_SIZE + 1)

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 10 MB or smaller.",
        )

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF.",
        )

    try:
        reader = PdfReader(BytesIO(contents))

        if reader.is_encrypted:
            raise HTTPException(
                status_code=422,
                detail="Password-protected PDFs are not supported yet.",
            )

        pages = [
            {
                "page_number": index + 1,
                "text": page.extract_text() or "",
            }
            for index, page in enumerate(reader.pages)
        ]

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please try another file.",
        ) from exc

    full_text = "\n\n".join(
        page["text"] for page in pages if page["text"].strip()
    )

    if not full_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No selectable text found. Scanned PDFs need OCR.",
        )

    chunks = chunk_text(full_text)

    return {
        "filename": file.filename,
        "page_count": len(pages),
        "character_count": len(full_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
        "pages": pages,
        "text": full_text,
    }
