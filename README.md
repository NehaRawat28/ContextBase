ContextBase – Intelligent RAG Knowledge Retrieval System
Overview:

ContextBase is an AI-powered knowledge retrieval system built using Retrieval-Augmented Generation (RAG) architecture. The system allows users to query personal or domain-specific documents and receive contextually grounded responses using semantic search and LLM-based answer generation.

The project combines embedding-based vector search with large language model inference to minimize hallucination and improve response relevance.

✨ Features:

📄 Document-based knowledge retrieval

🔍 Semantic search using vector embeddings

🤖 LLM-grounded response generation

🌍 Multi-backend support (OpenAI / Groq)

⚡ Fast similarity search using FAISS

🧠 Query preprocessing and retrieval pipeline

📌 Source-aware answers to reduce hallucination

💻 CLI-based interaction system

🏗️ System Architecture
User Query
   ↓
Query Processing Layer
   ↓
Embedding Generation
   ↓
Vector Similarity Search (FAISS)
   ↓
Context Ranking
   ↓
LLM Response Generation
   ↓
Final Answer with Source Reference
📦 Project Structure
data/                  → Knowledge base documents (.txt)
embeddings.py          → Document processing & embedding generation
retriever.py           → Vector search implementation
generator.py           → LLM response generation
main.py                → CLI entry point
requirements.txt       → Dependencies
setup.sh               → Environment setup script
run.sh                 → Execution launcher
🚀 Installation & Setup
1. Clone Repository
git clone <repo-url>
cd ContextBase
2. Setup Environment

Run automatic setup:

bash setup.sh

This will:

Create virtual environment

Install required dependencies

3. Configure API Keys

Create .env file:

OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

⚠️ Never commit .env file.

▶️ Running the Application
Interactive Mode
bash run.sh
Groq Backend (Free and Fast)
bash run.sh --backend groq
Retrieval Only Mode
bash run.sh --no-llm
Single Query Execution
bash run.sh --query "What is RAG?"
🧠 How It Works

Documents are split into chunks.

Each chunk is converted into vector embeddings.

Query is embedded and compared using cosine similarity.

Top-K relevant knowledge chunks are retrieved.

Context is injected into LLM prompt.

Final grounded answer is generated.

🔧 Configuration

Modify embedding and chunking parameters in embeddings.py:

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 75
🛠️ Technologies Used

Python 3.8+

Sentence Transformers

FAISS Vector Database

OpenAI / Groq APIs

NumPy

🔒 Security Notes

Add API keys inside .env file.

Do not commit secrets to GitHub.

Ensure .gitignore includes:

.env
venv/
__pycache__/
node_modules/
🎯 Future Improvements

Query translation and intent refinement layer

Hybrid search (semantic + keyword search)

Re-ranking of retrieved contexts

Multi-language support

Web-based UI interface

⭐ Project Goal

The goal of ContextBase is to improve information accessibility by combining retrieval systems with generative AI while reducing hallucinated responses.
