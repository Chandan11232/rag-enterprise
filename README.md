# RAG Enterprise Engine

Production-ready, local-first RAG microservice built with FastAPI, PostgreSQL + `pgvector` (hybrid search), sentence-transformers (dense embedding + cross-encoder reranking), and Ollama running **DeepSeek-Coder-V2:16b** (or compatible local models like DeepSeek-R1 / Qwen2.5), complete with a stunning **Streamlit Frontend Dashboard**.

---

## 1. High-Level System Architecture

```
                  ┌────────────────────────────────────────┐
                  │          FastAPI Microservice          │
                  │                                        │
User Query ──────►│ 1. Query Normalization & Cache Check   │
                  │ 2. Hybrid Search (Dense + BM25)        │◄─── PostgreSQL + pgvector
                  │ 3. Cross-Encoder Rerank (BGE-reranker) │
                  │ 4. Grounded Prompt Formulation         │
                  │ 5. Streaming Inference (HTTP / SSE)    │◄─── Ollama Server (DeepSeek-V2:16b)
                  └────────────────────────────────────────┘
                                      ▲
                                      │ Ingestion / Automation
                  ┌───────────────────┴────────────────────┐
                  │          DevOps / CI/CD Pipeline       │
                  │  GitHub Actions -> Pytest -> DockerHub  │
                  └────────────────────────────────────────┘
```

---

## 2. Tech Stack
- **Frontend Dashboard:** Streamlit (Real-time streaming chat, sidebar document ingestion, system health metrics)
- **API Framework:** FastAPI (Async, Pydantic v2)
- **Database & Vector Store:** PostgreSQL 16 with `pgvector` (HNSW indexing) & async SQLAlchemy
- **Embeddings & Reranking:** HuggingFace `sentence-transformers` (`BAAI/bge-small-en-v1.5` & `BAAI/bge-reranker-base`)
- **LLM Runtime:** Ollama (DeepSeek-Coder-V2:16b / DeepSeek-R1)
- **Testing & Quality:** Pytest, HTTPX, Ruff linter
- **DevOps:** Docker, Docker Compose, GitHub Actions CI/CD

---

## 3. Getting Started

### Quick Start
```bash
# 1. Start backend services (PostgreSQL + pgvector)
make up

# 2. Run the frontend dashboard
make frontend
```

### Accessing the Dashboard & API
- **Frontend UI:** `http://localhost:8501`
- **API Swagger Docs:** `http://localhost:8001/docs`
- **Health Check:** `http://localhost:8001/api/v1/health`
