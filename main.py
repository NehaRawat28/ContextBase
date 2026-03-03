"""
main.py
Personal Knowledge Base RAG — Main Entry Point
"""

import argparse
import os
from dotenv import load_dotenv

from embeddings import prepare_chunks_with_embeddings
from retriever import VectorStore, Retriever
from generator import Generator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()


# ─────────────────────────────────────────────
# FastAPI Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="ContextBase RAG API",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Request Model
# ─────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    k: int = 3


# ─────────────────────────────────────────────
# Global Pipeline Objects
# ─────────────────────────────────────────────
retriever = None
generator = None
DEFAULT_K = 3


# ─────────────────────────────────────────────
# Pipeline Builder
# ─────────────────────────────────────────────
def build_pipeline(
    backend: str,
    model: str | None,
    k: int,
    data_dir: str,
    no_llm: bool,
):
    chunks, embeddings, emb_model = prepare_chunks_with_embeddings(data_dir)

    store = VectorStore(dimension=emb_model.dimension)
    store.add(chunks, embeddings)

    retriever = Retriever(store, emb_model)

    generator = None
    if not no_llm:
        generator = Generator(backend=backend, model=model)

    return retriever, generator, k


# ─────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    global retriever, generator, DEFAULT_K

    print("🚀 Initialising RAG Pipeline...")

    retriever, generator, DEFAULT_K = build_pipeline(
        backend=os.getenv("LLM_BACKEND", "groq"),
        model=os.getenv("LLM_MODEL", None),
        k=3,
        data_dir="data",
        no_llm=False,
    )


# ─────────────────────────────────────────────
# Root Route
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "ContextBase RAG API is running 🚀"}


# ─────────────────────────────────────────────
# Query Endpoint
# ─────────────────────────────────────────────
@app.post("/query")
def query_api(request: QueryRequest):
    query = request.question
    k = request.k or DEFAULT_K

    # Retrieve
    results = retriever.retrieve(query, k=k)

    # Build context
    context = retriever.format_context(results)

    # Generate answer
    if generator:
        answer = generator.generate(
            context=context,
            question=query
        )
    else:
        answer = context

    # 🔥 Now returning sources
    return {
        "question": query,
        "answer": answer,
        "sources": results
    }


# ─────────────────────────────────────────────
# CLI Utilities (unchanged)
# ─────────────────────────────────────────────
def run_query(query: str, retriever: Retriever, generator, k: int) -> None:
    results = retriever.retrieve(query, k=k)
    context = retriever.format_context(results)

    if generator:
        answer = generator.generate(context=context, question=query)
        print("\nAnswer:\n", answer)
    else:
        print("\nRetrieved Context:\n", context)


def interactive_loop(retriever, generator, k: int) -> None:
    print("\nInteractive mode started. Type 'quit' to exit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        if not query:
            continue
        run_query(query, retriever, generator, k)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Personal Knowledge Base RAG System"
    )

    parser.add_argument("--backend", default="groq")
    parser.add_argument("--model", default=None)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--query", default=None)
    parser.add_argument("--no-llm", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    retriever, generator, k = build_pipeline(
        backend=args.backend,
        model=args.model,
        k=args.k,
        data_dir=args.data_dir,
        no_llm=args.no_llm,
    )

    if args.query:
        run_query(args.query, retriever, generator, k)
    else:
        interactive_loop(retriever, generator, k)


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()