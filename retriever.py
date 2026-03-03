"""
retriever.py
FAISS-backed vector store with MMR retrieval support.
"""

import os
import pickle
from typing import List, Dict

import numpy as np
import faiss

from embeddings import EmbeddingModel


# ── FAISS Vector Store ─────────────────────────────────────────────────────────
class VectorStore:
    """
    Wraps a FAISS index with chunk metadata for semantic retrieval.
    Uses IndexFlatIP (inner-product / cosine similarity) since embeddings
    are L2-normalized before insertion.
    """

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: List[Dict] = []
        self.embeddings: np.ndarray = None  # Store embeddings for MMR

    # ── Indexing ───────────────────────────────────────────────────────────────
    def add(self, chunks: List[Dict], embeddings: np.ndarray) -> None:
        assert embeddings.dtype == np.float32
        assert len(chunks) == embeddings.shape[0]

        self.index.add(embeddings)
        self.chunks.extend(chunks)

        # Save embeddings for MMR
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        print(f"✔ Indexed {len(chunks)} chunks "
              f"(total: {self.index.ntotal})")

    # ── Standard Search (returns raw for MMR) ──────────────────────────────────
    def search(self, query_embedding: np.ndarray, k: int = 10):
        """
        Returns raw FAISS scores and indices for MMR selection.
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, k)
        return scores[0], indices[0]

    # ── Persistence ────────────────────────────────────────────────────────────
    def save(self, index_path="faiss.index",
             meta_path="chunks_meta.pkl") -> None:
        faiss.write_index(self.index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump({
                "chunks": self.chunks,
                "dimension": self.dimension,
                "embeddings": self.embeddings
            }, f)
        print("✔ Index saved")

    @classmethod
    def load(cls, index_path="faiss.index",
             meta_path="chunks_meta.pkl") -> "VectorStore":
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError("Index or metadata missing")

        with open(meta_path, "rb") as f:
            meta = pickle.load(f)

        store = cls(meta["dimension"])
        store.index = faiss.read_index(index_path)
        store.chunks = meta["chunks"]
        store.embeddings = meta["embeddings"]

        print(f"✔ Loaded {store.index.ntotal} vectors")
        return store


# ── Retriever with MMR ─────────────────────────────────────────────────────────
class Retriever:
    """
    High-level retriever with MMR (Max Marginal Relevance).
    """

    def __init__(self, vector_store: VectorStore, emb_model: EmbeddingModel):
        self.store = vector_store
        self.emb_model = emb_model

    # ── Main Retrieve Function (MMR) ───────────────────────────────────────────
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve using MMR (Max Marginal Relevance).
        """

        query_embedding = self.emb_model.encode([query])[0]

        # Candidate pool
        candidate_k = max(k * 3, 10)
        scores, indices = self.store.search(query_embedding, k=candidate_k)

        candidates = [
            (idx, score)
            for idx, score in zip(indices, scores)
            if idx != -1
        ]

        selected = []
        selected_indices = []

        all_embeddings = self.store.embeddings
        lambda_param = 0.7

        while len(selected_indices) < min(k, len(candidates)):

            best_score = -np.inf
            best_candidate = None

            for idx, relevance in candidates:
                if idx in selected_indices:
                    continue

                diversity = 0
                for sel_idx in selected_indices:
                    sim = np.dot(
                        all_embeddings[idx],
                        all_embeddings[sel_idx]
                    )
                    diversity = max(diversity, sim)

                mmr_score = (
                    lambda_param * relevance
                    - (1 - lambda_param) * diversity
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_candidate = (idx, relevance)

            if best_candidate is None:
                break

            selected_indices.append(best_candidate[0])
            selected.append(best_candidate)

        results = []

        for rank, (idx, score) in enumerate(selected, start=1):
            chunk = self.store.chunks[idx]

            results.append({
                "rank": rank,
                "score": float(score),
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
            })

        return results

    # ── Context Formatting ─────────────────────────────────────────────────────
    def format_context(self, results: List[Dict]) -> str:
        parts = []
        for r in results:
            parts.append(
                f"[Source: {r['source']} | "
                f"Chunk {r['chunk_id']} | "
                f"Score: {r['score']:.4f}]\n"
                f"{r['text']}"
            )
        return "\n\n---\n\n".join(parts)


# ── Standalone Demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from embeddings import prepare_chunks_with_embeddings

    chunks, embeddings, emb_model = prepare_chunks_with_embeddings()

    store = VectorStore(dimension=emb_model.dimension)
    store.add(chunks, embeddings)

    retriever = Retriever(store, emb_model)

    query = "What are the limitations of LLMs?"
    print(f"\nQuery: {query}\n")

    results = retriever.retrieve(query, k=3)

    for r in results:
        print(f"Rank {r['rank']} | Score {r['score']:.4f} | "
              f"{r['source']} (chunk {r['chunk_id']})")
        print(f"Preview: {r['text'][:120]}...\n")