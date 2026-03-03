from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from embeddings import prepare_chunks_with_embeddings
from retriever import VectorStore, Retriever
from generator import Generator

# Load env
load_dotenv()

app = FastAPI(title="ContextBase API")

# ── Load RAG Pipeline Once (Startup) ─────────────────────
print("Loading RAG pipeline...")

chunks, embeddings, emb_model = prepare_chunks_with_embeddings("data")

store = VectorStore(dimension=emb_model.dimension)
store.add(chunks, embeddings)

retriever = Retriever(store, emb_model)

generator = Generator(
    backend=os.getenv("LLM_BACKEND", "groq"),
    model=os.getenv("LLM_MODEL", None)
)

print("RAG pipeline ready.")

# ── Request Model ─────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    k: int = 3

# ── API Endpoint ──────────────────────────────────────────
@app.post("/query")
def query_rag(request: QueryRequest):
    results = retriever.retrieve(request.question, k=request.k)
    context = retriever.format_context(results)

    try:
        answer = generator.generate(context=context, question=request.question)
    except Exception as e:
        return {
            "error": str(e),
            "sources": results
        }

    return {
        "answer": answer,
        "sources": results
    }