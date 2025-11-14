# Project Context

## Purpose
Smart Water Knowledge System (智能水利知识库管理系统) for dam safety and hydraulic engineering. The platform ingests domain documents, builds a searchable knowledge base and knowledge graph, and provides domain‑aware Q&A, analysis dashboards, and task automation for operations teams.

Primary goals:
- Reliable knowledge ingestion (PDF/Word/Images) with OCR and structure extraction
- Hybrid retrieval: vector stores (Milvus/Chroma/LightRAG) + graph (Neo4j)
- Domain‑aware chat and tools via agents (LangGraph)
- Secure multi‑user access with roles and auditability
- Easy local and containerized deployment

## Tech Stack
- Backend: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, SQLite (default)
- Agents: LangGraph (+ LangChain components), async checkpointers (SQLite/In‑Memory)
- Knowledge storage: Milvus, Chroma, LightRAG; Graph DB: Neo4j; Object storage: MinIO
- Document parsing: LightRAG, MinerU (sglang server), PaddleOCR PP‑Structure‑V3, RapidOCR, PyMuPDF, python‑docx
- Frontend: Vue 3, Vite, Ant Design Vue, Pinia, Vue Router, ECharts/Sigma/G6 for graphs/visualization
- Docs: VitePress
- Tooling: Docker Compose; Logging with Loguru; Lint/format with Ruff; Tests with pytest/pytest‑asyncio; Python env via uv; Web deps via pnpm

## Project Conventions

### Code Style
- Python: Ruff for lint and format (`line-length = 120`, import sorting enabled). Type hints preferred. Use `src.utils.logging_config.logger` (Loguru) for logging.
- Vue: ESLint + Prettier. Keep components small, composition API, co‑locate styles.
- Naming: snake_case for functions/vars, PascalCase for classes, kebab‑case for files (Vue components use PascalCase filenames where appropriate).

### Architecture Patterns
- API layer: FastAPI app in `server/` with feature‑oriented routers under `server/routers` (auth, chat, dashboard, knowledge, graph, system, tasks).
- Services/utilities: Business logic and helpers in `server/services` and `server/utils`.
- Domain core: Agent and knowledge logic in `src/` (agents, config, storage, utils). Agents are implemented with LangGraph and optional SQLite checkpointers for history.
- Configuration: Centralized config in `src/config` (YAML + `.env`) with sensible defaults, persisted under `saves/`.
- Storage: `src/storage/db` (SQLAlchemy + SQLite by default), `src/storage/minio`, vector/graph backends per capability.
- Separation of concerns: Routers -> service/manager -> storage; agents consume config and toolkits.

### Testing Strategy
- Framework: pytest with `pytest-asyncio`, `pytest-httpx`, and markers (`auth`, `integration`, `slow`).
- Layout: API route tests in `test/api/`, storage and utility tests alongside.
- Commands: `pytest -v` locally; `make router-tests` to run API tests in Docker. See `pyproject.toml` for defaults.

### Git Workflow
- Branching: feature branches from `main`, named `feat/<short>`, `fix/<short>`, `chore/<short>`.
- Commits: Conventional Commits style (feat, fix, chore, docs, refactor, test, perf).
- Reviews: Open PRs for non‑trivial changes. Use OpenSpec proposals for any new capability, breaking change, or architecture change. Do not implement until proposal is approved.

## Domain Context
- Focus: hydraulic engineering and dam safety operations.
- Data: Chinese documents are common; OCR and table extraction quality matters.
- Core scenarios: expert Q&A, incident analysis, dashboarding, graph exploration, ingestion pipelines.

## Important Constraints
- At least one model provider must be configured (e.g., `OPENAI_API_KEY`, `SILICONFLOW_API_KEY`, etc.); otherwise startup asserts.
- Default persistence under `saves/` (configs, logs, SQLite DB, agent state); ensure write access in deployment.
- Offline/air‑gapped friendly: supports local model dirs via `MODEL_DIR`; external web search is optional and off by default.
- Security: JWT auth for UI/API; CORS enabled; login rate limiting; content guard switches available in config.

## External Dependencies
- Databases/services (Docker Compose defaults):
  - Neo4j: `bolt://graph:7687` (env: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`)
  - Milvus: `http://milvus:19530` (env: `MILVUS_URI`, `MILVUS_TOKEN`)
  - MinIO: `http://milvus-minio:9000` (env: `MINIO_URI`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`)
  - MinerU OCR: `http://mineru:30000` (env: `MINERU_OCR_URI`)
  - PaddleOCR service: `http://paddlex:8080` (env: `PADDLEX_URI`)
- LLM providers: configured via `src/config/static/models.yaml` and `.env` variables; supports multiple vendors.
