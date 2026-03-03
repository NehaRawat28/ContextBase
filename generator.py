"""
generator.py
Grounded answer generation using an LLM (OpenAI or Groq).
The LLM is instructed to answer ONLY from the retrieved context.
"""
from dotenv import load_dotenv


load_dotenv()

import os
from typing import List, Dict, Optional

# ── Prompt Template ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions strictly based on the provided context documents.

RULES:
1. Answer ONLY using information from the context provided below.
2. If the answer is not found in the context, respond exactly with: "Not found in knowledge base."
3. Do NOT use your internal training knowledge to supplement answers.
4. Be concise, accurate, and cite the source filename when possible.
5. If multiple chunks support the answer, synthesize them into a coherent response."""

USER_PROMPT_TEMPLATE = """Context Documents:
{context}

---

Question: {question}

Answer (based strictly on the context above):"""


# ── Backend helpers ────────────────────────────────────────────────────────────
def _build_messages(context: str, question: str) -> List[Dict]:
    """Build the messages list for a chat-completion call."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT_TEMPLATE.format(
            context=context, question=question)},
    ]


def _call_openai(messages: List[Dict], model: str, temperature: float,
                 max_tokens: int) -> str:
    """Call the OpenAI ChatCompletion API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Export it with:  export OPENAI_API_KEY='sk-...'"
        )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _call_groq(messages: List[Dict], model: str, temperature: float,
               max_tokens: int) -> str:
    """Call the Groq ChatCompletion API."""
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("groq package not installed. Run: pip install groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY environment variable is not set.\n"
            "Export it with:  export GROQ_API_KEY='gsk_...'"
        )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


# ── Generator ──────────────────────────────────────────────────────────────────
class Generator:
    """
    Wraps an LLM API to produce context-grounded answers.

    Supported backends:
        "openai" → any OpenAI-compatible model (gpt-4o, gpt-3.5-turbo …)
        "groq"   → Groq-hosted open-source models (llama3-8b-8192 …)
    """

    DEFAULTS = {
        "openai": "gpt-3.5-turbo",
        "groq":   "llama3-8b-8192",
    }

    def __init__(
        self,
        backend: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ):
        backend = backend.lower()
        if backend not in self.DEFAULTS:
            raise ValueError(f"Unknown backend '{backend}'. Choose 'openai' or 'groq'.")

        self.backend = backend
        self.model = model or self.DEFAULTS[backend]
        self.temperature = temperature
        self.max_tokens = max_tokens
        print(f"  ✔ Generator: backend={backend}, model={self.model}")

    def generate(self, context: str, question: str) -> str:
        """
        Generate a grounded answer.

        Args:
            context:  Retrieved context string (formatted chunks)
            question: User's question

        Returns:
            LLM-generated answer string
        """
        messages = _build_messages(context, question)

        if self.backend == "openai":
            return _call_openai(messages, self.model, self.temperature, self.max_tokens)
        elif self.backend == "groq":
            return _call_groq(messages, self.model, self.temperature, self.max_tokens)


# ── Standalone demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_context = """[Source: llm_limitations.txt | Chunk 0 | Score: 0.85]
    LLMs suffer from hallucination — generating confident but incorrect facts.
    They also have a knowledge cutoff, limited context window, and cannot access private data."""

    sample_question = "What are limitations of LLMs?"

    backend = os.getenv("LLM_BACKEND", "openai")
    gen = Generator(backend=backend)
    answer = gen.generate(context=sample_context, question=sample_question)
    print(f"\nAnswer:\n{answer}")