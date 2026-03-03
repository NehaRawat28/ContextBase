import streamlit as st
import os
from dotenv import load_dotenv

from embeddings import prepare_chunks_with_embeddings
from retriever import VectorStore, Retriever
from generator import Generator

# ── Load env ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="ContextBase",
    page_icon="📚",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────
st.title("📚 ContextBase")
st.caption("Modular Retrieval-Augmented Generation System")

# ── Sidebar Controls ─────────────────────────────────────
st.sidebar.header("⚙ Settings")

k_value = st.sidebar.slider("Top-K Retrieval", 1, 10, 3)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Backend")
st.sidebar.markdown(f"**LLM Backend:** `{os.getenv('LLM_BACKEND', 'groq')}`")
st.sidebar.markdown(f"**Model:** `{os.getenv('LLM_MODEL', 'default')}`")

st.sidebar.markdown("---")
st.sidebar.info("This system answers only from the indexed knowledge base.")

# ── Cache Pipeline ───────────────────────────────────────
@st.cache_resource
def load_pipeline():
    with st.spinner("Loading knowledge base..."):
        chunks, embeddings, emb_model = prepare_chunks_with_embeddings("data")

        store = VectorStore(dimension=emb_model.dimension)
        store.add(chunks, embeddings)

        retriever = Retriever(store, emb_model)
        generator = Generator(
            backend=os.getenv("LLM_BACKEND", "groq"),
            model=os.getenv("LLM_MODEL", None)
        )

        return retriever, generator

retriever, generator = load_pipeline()

# ── Session State ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display Chat History ─────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat Input ───────────────────────────────────────────
query = st.chat_input("Ask something about your knowledge base...")

if query:
    # User message
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Retrieving & generating answer..."):
        results = retriever.retrieve(query, k=k_value)
        context = retriever.format_context(results)

        try:
            answer = generator.generate(context=context, question=query)
        except Exception as e:
            answer = f"⚠ Error generating answer:\n\n{e}"

    # Assistant message
    with st.chat_message("assistant"):
        st.markdown(answer)

        with st.expander("📄 View Retrieved Sources"):
            for r in results:
                st.markdown(
                    f"""
                    **Rank {r['rank']}**  
                    Score: `{r['score']:.4f}`  
                    File: `{r['source']}`  
                    Chunk: `{r['chunk_id']}`  

                    > {r['text'][:400]}...
                    """
                )

    st.session_state.messages.append({"role": "assistant", "content": answer})