
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load the API key from backend/.env
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check backend/.env"
        )

    return genai.Client(api_key=api_key)


def embed_text(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """Convert text into an embedding vector using Gemini."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    client = get_client()

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=768,
        ),
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embedding.")

    return response.embeddings[0].values
