"""
embeddings.py
Handles document loading, text chunking, and embedding generation.
"""

import os
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np


# ── Configuration ──────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 400        # approximate word count per chunk
CHUNK_OVERLAP = 75      # words shared between adjacent chunks
DATA_DIR = "data"


# ── Document Loading ───────────────────────────────────────────────────────────
def load_documents(data_dir: str = DATA_DIR) -> List[Dict]:
    """
    Load all .txt files from the data directory.

    Returns:
        List of dicts: [{text: str, source: str}, ...]
    """
    documents = []

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found.")

    txt_files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]

    if not txt_files:
        raise ValueError(f"No .txt files found in '{data_dir}'.")

    for filename in sorted(txt_files):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        documents.append({"text": text, "source": filename})
        print(f"  ✔ Loaded: {filename} ({len(text.split())} words)")

    return documents


# ── Text Chunking ──────────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping word-level chunks.

    Args:
        text:       Full document text
        chunk_size: Target number of words per chunk
        overlap:    Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # slide forward with overlap

    return chunks


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Chunk all loaded documents and preserve source metadata.

    Returns:
        List of dicts: [{text: str, source: str, chunk_id: int}, ...]
    """
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "chunk_id": i,
            })

    return all_chunks


# ── Embedding Generation ───────────────────────────────────────────────────────
class EmbeddingModel:
    """Wraps a SentenceTransformer model for encoding text to vectors."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        print(f"\n  Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"  ✔ Model loaded (dim={self.model.get_sentence_embedding_dimension()})")

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str], batch_size: int = 64,
               normalize: bool = True) -> np.ndarray:
        """
        Encode a list of texts into L2-normalized embedding vectors.

        Args:
            texts:      List of strings to encode
            batch_size: Batch size for encoding
            normalize:  Whether to L2-normalize (needed for cosine similarity)

        Returns:
            np.ndarray of shape (len(texts), dimension), dtype float32
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )
        return embeddings.astype("float32")


# ── Public Helper ──────────────────────────────────────────────────────────────
def prepare_chunks_with_embeddings(
    data_dir: str = DATA_DIR,
) -> Tuple[List[Dict], np.ndarray, EmbeddingModel]:
    """
    Full pipeline: load → chunk → embed.

    Returns:
        chunks:      List of chunk dicts (text, source, chunk_id)
        embeddings:  np.ndarray of shape (n_chunks, dim)
        emb_model:   EmbeddingModel instance (reuse for query encoding)
    """
    print("\n[1/3] Loading documents …")
    docs = load_documents(data_dir)

    print("\n[2/3] Chunking documents …")
    chunks = chunk_documents(docs)
    print(f"  ✔ Total chunks: {len(chunks)}")

    emb_model = EmbeddingModel()

    print("\n[3/3] Generating embeddings …")
    texts = [c["text"] for c in chunks]
    embeddings = emb_model.encode(texts)
    print(f"  ✔ Embeddings shape: {embeddings.shape}")

    return chunks, embeddings, emb_model


if __name__ == "__main__":
    chunks, embeddings, model = prepare_chunks_with_embeddings()
    print(f"\nSample chunk from '{chunks[0]['source']}':\n")
    print(chunks[0]["text"][:300], "…")