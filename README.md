# RAG Enterprise Engine

Production-ready, local-first RAG microservice built with FastAPI, PostgreSQL + `pgvector` (hybrid search), sentence-transformers (dense embedding + cross-encoder reranking), and Ollama running **DeepSeek-Coder-V2:16b** (or compatible local models like DeepSeek-R1 / Qwen2.5).

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
- **API Framework:** FastAPI (Async, Pydantic v2)
- **Database & Vector Store:** PostgreSQL 16 with `pgvector` (HNSW indexing) & async SQLAlchemy
- **Embeddings & Reranking:** HuggingFace `sentence-transformers` (`BAAI/bge-small-en-v1.5` & `BAAI/bge-reranker-base`)
- **LLM Runtime:** Ollama (DeepSeek-Coder-V2:16b / DeepSeek-R1)
- **Testing & Quality:** Pytest, HTTPX, Ruff linter
- **DevOps:** Docker, Docker Compose, GitHub Actions CI/CD

---

## 3. Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Quick Start with Docker Compose
```bash
# 1. Start services
make up

# 2. Pull DeepSeek-Coder-V2 inside Ollama container
make pull-model

# 3. Check health
curl http://localhost:8000/api/v1/health
```

### Running Tests Locally
```bash
pip install -r requirements.txt
pytest -v
```
