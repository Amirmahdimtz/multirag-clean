# MultiRAG Clean

![CI](https://github.com/Amirmahdimtz/multirag-clean/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/Amirmahdimtz/multirag-clean/actions/workflows/codeql.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Release](https://img.shields.io/github/v/release/Amirmahdimtz/multirag-clean)

MultiRAG Clean is a FastAPI service for managing users, datasets, vector search,
RAG systems, access control, and streamed chat. It is a layered rewrite of the
previous `multirag-main` project and uses `dependency_injector` to keep object
construction and dependency wiring outside business code.

The project supports:

- admin datasets and user-owned datasets;
- PDF, DOCX, TXT, and CSV files;
- chunk preview, vectorization, similarity search, download, and filename APIs;
- simple chat, shared RAG chat, and user-specific RAG chat;
- API-key authentication for admin and user operations;
- SQLite and fake providers for lightweight local checks;
- PostgreSQL/pgvector, Jina embeddings, and vLLM for production;
- Docker Compose deployment on port `2011` by default.

## Architecture

The source code is divided into five layers:

| Layer | Location | Responsibility |
| --- | --- | --- |
| Host | `src/host/` | Application entry point and top-level startup |
| Application | `src/application/` | FastAPI controllers, DTOs, authentication dependencies, exception mapping, and router registration |
| Core | `src/core/` | Business rules, use-case orchestration, contracts, LLM selection, and application exceptions |
| Infrastructure | `src/infrastructure/` | Database context, repositories, file storage, document processing, embeddings, vector stores, and vLLM client |
| Domain | `src/domain/` | Entities, value objects, and enums |

Dependency construction is centralized in Collection containers:

- `InfrastructureCollection`: configuration, database context, repositories,
  storage, embedding, vector-store, document-processing, and chat-model
  providers.
- `CoreCollection`: business services and factories built from core contracts.
- `ApplicationCollection`: controllers, API-key dependencies, and `WebService`.
- `WebHostCollection`: starts the composed application.

Controllers are registered explicitly through `ApplicationCollection.controllers`.
Repositories receive `DbContext` and open a session per operation instead of
holding a long-lived SQLAlchemy session.

### Runtime flow

```text
HTTP request
  -> Application controller
  -> Core business service
  -> Core repository/service contract
  -> Infrastructure implementation
  -> PostgreSQL/SQLite, file storage, pgvector, Jina, or vLLM
```

## Project structure

```text
multirag-clean/
├── alembic/
├── config/config.yaml
├── deploy/
├── docs/
├── src/
│   ├── application/
│   ├── core/
│   ├── domain/
│   ├── host/
│   └── infrastructure/
├── .env.example
├── Dockerfile
├── docker-compose.yaml
├── main.py
└── requirements.txt
```

## Requirements

### Local development

- Python 3.10
- `pip` and Python virtual environments

The default local profile uses SQLite, a deterministic fake embedding service,
a SQLite-backed vector store, and a fake streaming chat model. It does not
require PostgreSQL, a GPU, vLLM, or a model download.

### Production

- 64-bit Linux
- Docker Engine and the Docker Compose plugin
- NVIDIA driver and NVIDIA Container Toolkit
- enough disk space for container images and model caches
- an NVIDIA GPU compatible with the selected vLLM model
- a Hugging Face token if the selected model is gated

The supplied production profile is intended for one NVIDIA A100-SXM4 40 GB and
uses `google/gemma-4-31B-it-qat-w4a16-ct`. Revalidate the vLLM image, model,
context length, and GPU-memory settings before using a different server.

## Local installation

Create and activate an isolated environment:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PowerShell activation on Windows:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a local `.env` file with the following minimal values:

```dotenv
MULTIRAG_APPLICATION_HOST=127.0.0.1
MULTIRAG_APPLICATION_PORT=8000
MULTIRAG_DATABASE_URL=sqlite+aiosqlite:///./test.db
MULTIRAG_DATABASE_ECHO_SQL=false
MULTIRAG_SECURITY_ENABLED=false
MULTIRAG_EMBEDDING_PROVIDER=fake
MULTIRAG_VECTOR_STORE_PROVIDER=sqlite_json
MULTIRAG_LLM_PROVIDER=fake
MULTIRAG_STORAGE_BASE_PATH=storage
```

Do not commit or deliver the generated `.env`, `test.db`, `storage/`, or local
virtual environment.

## Development checks

Run the lightweight core unit test suite from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
ruff check src tests alembic
```

GitHub Actions also runs correctness-focused Ruff checks, compiles `src/`,
`tests/`, and `alembic/`, and runs the test suite for pull requests and
pushes to `main`.

Database migrations are versioned with Alembic. With
`MULTIRAG_DATABASE_URL` configured for a disposable development database:

```bash
alembic upgrade head
alembic check
```

`alembic check` should report no pending schema operations.

## Local execution

Run the service from the project root:

```bash
python main.py
```

Default local URLs:

- API: `http://127.0.0.1:8000/api/v1`
- health: `http://127.0.0.1:8000/api/v1/health/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

If port 8000 is already in use, stop the other process or change
`MULTIRAG_APPLICATION_PORT`.

## Docker execution

Create the production environment file:

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

Replace every `CHANGE_ME` value. In particular, configure the PostgreSQL
password and URL, MultiRAG API keys, vLLM API key, and Hugging Face token.

Validate and start the stack:

```bash
docker compose --env-file .env config --quiet
docker compose --env-file .env build --pull app
docker compose --env-file .env pull postgres vllm
docker compose --env-file .env up -d postgres
docker compose --env-file .env run --rm --no-deps app alembic upgrade head
docker compose --env-file .env up -d
chmod +x deploy/healthcheck.sh
./deploy/healthcheck.sh
```

The Compose stack contains:

| Service | Purpose | Host exposure |
| --- | --- | --- |
| `app` | FastAPI MultiRAG service | port `2011` by default |
| `postgres` | PostgreSQL 16 with pgvector | internal network only |
| `vllm` | OpenAI-compatible LLM server | internal network only |

PostgreSQL data, uploaded files, vLLM model cache, and embedding model cache are
stored in named Docker volumes. The application talks to vLLM through
`http://vllm:8000/v1`. Jina embeddings run inside the application container on
CPU; GPU access is reserved for vLLM.

Useful commands:

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs -f --tail=200 app
docker compose --env-file .env logs -f --tail=200 vllm
docker compose --env-file .env logs -f --tail=200 postgres
docker compose --env-file .env down
```

`docker compose down` preserves named volumes. Do not run
`docker compose down -v` in production unless permanent data deletion is
intentional and a verified backup exists.

For backup, updates, rollback, troubleshooting, security, and optional systemd
setup, see [docs/production-deployment.md](docs/production-deployment.md).

## Configuration

`config/config.yaml` defines the configuration structure. Values in the form
`${VARIABLE:default}` are resolved from environment variables. `ConfigReader`
also loads a project-root `.env` file when it exists, without overriding
variables already supplied by the operating system or container.

### Main environment variables

| Group | Variables |
| --- | --- |
| Application | `MULTIRAG_APPLICATION_HOST`, `MULTIRAG_APPLICATION_PORT` |
| Database | `MULTIRAG_DATABASE_URL`, `MULTIRAG_DATABASE_ECHO_SQL`, `MULTIRAG_DATABASE_POOL_SIZE`, `MULTIRAG_DATABASE_MAX_OVERFLOW`, `MULTIRAG_DATABASE_POOL_PRE_PING`, `MULTIRAG_DATABASE_POOL_RECYCLE_SECONDS` |
| Security | `MULTIRAG_SECURITY_ENABLED`, `MULTIRAG_ADMIN_API_KEYS`, `MULTIRAG_USER_API_KEYS` |
| Uploads | `MULTIRAG_STORAGE_BASE_PATH`, `MULTIRAG_UPLOAD_MAX_FILE_SIZE_MB`, `MULTIRAG_UPLOAD_ALLOWED_EXTENSIONS` |
| Chunking | `MULTIRAG_CHUNK_SIZE`, `MULTIRAG_CHUNK_OVERLAP` |
| Retrieval | `MULTIRAG_RAG_K_RETRIEVAL`, `MULTIRAG_RAG_SCORE_THRESHOLD` |
| Embedding | `MULTIRAG_EMBEDDING_PROVIDER`, `MULTIRAG_EMBEDDING_MODEL`, `MULTIRAG_EMBEDDING_VECTOR_SIZE`, `MULTIRAG_EMBEDDING_DEVICE`, `MULTIRAG_EMBEDDING_OFFLINE`, `MULTIRAG_EMBEDDING_LOCAL_PATH`, `MULTIRAG_EMBEDDING_NORMALIZE` |
| Vector store | `MULTIRAG_VECTOR_STORE_PROVIDER`, `MULTIRAG_PGVECTOR_TABLE_PREFIX`, `MULTIRAG_PGVECTOR_VECTOR_SIZE`, `MULTIRAG_PGVECTOR_BATCH_SIZE`, `MULTIRAG_PGVECTOR_HNSW_ENABLED` |
| LLM | `MULTIRAG_LLM_PROVIDER`, `MULTIRAG_LLM_MODEL`, `MULTIRAG_LLM_BASE_URL`, `MULTIRAG_LLM_API_KEY`, `MULTIRAG_LLM_TEMPERATURE`, `MULTIRAG_LLM_MAX_TOKENS`, `MULTIRAG_LLM_TOP_P`, `MULTIRAG_LLM_TOP_K`, `MULTIRAG_LLM_TIMEOUT_SECONDS` |

API-key lists and allowed extensions are JSON values:

```dotenv
MULTIRAG_ADMIN_API_KEYS=["admin-key-1","admin-key-2"]
MULTIRAG_USER_API_KEYS=[{"api_key":"user-key-1","user_id":"00000000-0000-0000-0000-000000000000"}]
MULTIRAG_UPLOAD_ALLOWED_EXTENSIONS=["pdf","docx","txt","csv"]
```

Authenticated requests use:

```http
Authorization: Bearer <API_KEY>
```

For the Jina/pgvector production profile, these dimensions must agree with the
real embedding output:

```dotenv
MULTIRAG_EMBEDDING_VECTOR_SIZE=1024
MULTIRAG_PGVECTOR_VECTOR_SIZE=1024
```

Changing the embedding provider, model, normalization, or dimension requires
re-vectorizing existing datasets.

## API endpoints

All paths below are relative to the default `/api/v1` prefix.

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health/` | Public | Service health |
| GET | `/health/info` | Public | Application information |
| POST | `/admin/users/` | Admin | Create a user |
| GET | `/admin/users/` | Admin | List users |
| POST | `/admin/datasets/upload` | Admin | Upload an admin dataset |
| GET | `/admin/datasets/` | Admin | List admin datasets |
| POST | `/admin/datasets/{dataset_id}/vectorize` | Admin | Vectorize an admin dataset |
| GET | `/admin/datasets/{dataset_id}/search` | Admin | Search an admin dataset |
| GET | `/admin/datasets/{dataset_id}/chunks/preview` | Admin | Preview extracted chunks |
| GET | `/admin/datasets/{dataset_id}/download` | Admin | Download the original dataset |
| GET | `/admin/datasets/{dataset_id}/filename` | Admin | Get the original filename |
| POST | `/user/datasets/upload` | User | Upload a user-owned dataset |
| GET | `/user/datasets/` | User | List the authenticated user's datasets |
| POST | `/user/datasets/{dataset_id}/vectorize` | User | Vectorize an owned dataset |
| GET | `/user/datasets/{dataset_id}/search` | User | Search an owned dataset |
| DELETE | `/user/datasets/{dataset_id}` | User | Delete an owned dataset |
| POST | `/admin/rag-systems` | Admin | Create a RAG system from a vectorized admin dataset |
| GET | `/admin/rag-systems` | Admin | List RAG systems |
| GET | `/admin/rag-systems/{rag_system_id}` | Admin | Get a RAG system |
| DELETE | `/admin/rag-systems/{rag_system_id}` | Admin | Delete a RAG system |
| GET | `/admin/rag-systems/{rag_system_id}/search` | Admin | Search through a RAG system |
| POST | `/admin/rag-systems/{rag_system_id}/ask` | Admin | Generate an answer with retrieved contexts |
| POST | `/admin/rag_access` | Admin | Grant a user access to a RAG system |
| GET | `/admin/rag_access/users` | Admin | List users assigned to a RAG system |
| GET | `/admin/rag_access/rag_systems` | Admin | List RAG systems assigned to a user |
| DELETE | `/admin/rag_access` | Admin | Revoke RAG access |
| POST | `/user/chat/create` | User or admin | Create a `simple`, `rag`, or `user_rag` session |
| GET | `/user/chat` | Same user or admin | List a user's sessions |
| POST | `/user/chat/history` | Same user or admin | Get a session's history using query parameters |
| DELETE | `/user/chat` | Same user or admin | Delete a session using query parameters |
| POST | `/user/chat` | Same user or admin | Stream a response as NDJSON |

Swagger UI contains the authoritative request and response schemas generated
from the running code.

## Local end-to-end test scenario

The following scenario uses the local fake providers and disabled security. It
validates the database, upload, chunking, vector search, RAG access, session
creation, and NDJSON streaming path without downloading an AI model.

1. Start the application and verify health:

   ```bash
   curl -fsS http://127.0.0.1:8000/api/v1/health/
   ```

2. Create a user and save the returned `data.id` as `USER_ID`:

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/admin/users/ \
     -H 'Content-Type: application/json' \
     -d '{"username":"smoke-test-user"}'
   ```

3. Upload the included sample and save the returned `data.id` as `DATASET_ID`:

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/admin/datasets/upload \
     -F 'name=smoke-test-dataset' \
     -F 'expertise=testing' \
     -F 'file=@rag-test.txt'
   ```

4. Vectorize and search the dataset:

   ```bash
   curl -sS -X POST \
     "http://127.0.0.1:8000/api/v1/admin/datasets/${DATASET_ID}/vectorize"

   curl -sS --get \
     "http://127.0.0.1:8000/api/v1/admin/datasets/${DATASET_ID}/search" \
     --data-urlencode 'query=authorized user access' \
     --data-urlencode 'limit=5' \
     --data-urlencode 'score_threshold=0'
   ```

5. Create a RAG system and save the returned `data.id` as `RAG_SYSTEM_ID`:

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/admin/rag-systems \
     -H 'Content-Type: application/json' \
     -d "{\"name\":\"smoke-test-rag\",\"dataset_id\":\"${DATASET_ID}\",\"description\":\"Local smoke test\"}"
   ```

6. Grant access to the user:

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/admin/rag_access \
     -H 'Content-Type: application/json' \
     -d "{\"user_id\":\"${USER_ID}\",\"rag_system_id\":\"${RAG_SYSTEM_ID}\"}"
   ```

7. Create a RAG chat session and save `data.id` as `SESSION_ID`:

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/user/chat/create \
     -H 'Content-Type: application/json' \
     -d "{\"user_id\":\"${USER_ID}\",\"name\":\"smoke-test-chat\",\"llm_type\":\"rag\",\"rag_system_id\":\"${RAG_SYSTEM_ID}\"}"
   ```

8. Stream a response:

   ```bash
   curl -N -sS -X POST http://127.0.0.1:8000/api/v1/user/chat \
     -H 'Content-Type: application/json' \
     -d "{\"user_id\":\"${USER_ID}\",\"session_id\":\"${SESSION_ID}\",\"user_prompt\":\"What is MultiRAG?\",\"llm_type\":\"rag\",\"rag_system_id\":\"${RAG_SYSTEM_ID}\"}"
   ```

When security is enabled, add `Authorization: Bearer <key>` to every protected
request. A user API key may only access the `user_id` assigned to that key;
admin keys may perform cross-user administration.

## Differences from `multirag-main`

| Area | Previous project | Clean rewrite |
| --- | --- | --- |
| Structure | Feature/utility-oriented `src` and separate `web` package | Explicit host, application, core, infrastructure, and domain layers |
| Dependency construction | Dependencies created across application code | Central Collection containers using `dependency_injector` |
| Business dependencies | Concrete implementations frequently visible to calling code | Core contracts with infrastructure implementations wired at composition time |
| Database access | Previous project-specific operations | Repository pattern with `DbContext` and per-method async sessions |
| Chat modes | Original simple/RAG behavior | `simple`, shared `rag`, and user-owned `user_rag` sessions with history and deletion |
| File behavior | Previous upload/vectorization flow | Validated PDF, DOCX, TXT, and CSV upload plus download, filename, metadata, and chunk preview |
| Authorization | Earlier admin/user flow | Bearer API keys, user binding, RAG grants, and ownership checks |
| LLM deployment | Ollama-based Compose service | vLLM OpenAI-compatible service isolated on the internal Docker network |
| Vector storage | PostgreSQL/pgvector-oriented deployment | Selectable SQLite JSON for local checks or pgvector for production |
| Embeddings | Jina integration | Selectable fake local embedding or Jina v3 inside the app container |
| Deployment | Older Docker/systemd setup | Multi-stage non-root image, health checks, restart policy, persistent volumes, and server-specific production guide |

The rewrite preserves the original project's main operational goals while
changing the internal architecture to the company's layered Dependency
Injection style.

## Releases

The latest tagged release is [v0.1.0](https://github.com/Amirmahdimtz/multirag-clean/releases/tag/v0.1.0).
Release checks and maintenance policy are documented in
[docs/maintenance.md](docs/maintenance.md).

## Project maintenance

The public maintenance plan is tracked in [ROADMAP.md](ROADMAP.md). Notable
changes are recorded in [CHANGELOG.md](CHANGELOG.md), maintainer release checks
are documented in [docs/maintenance.md](docs/maintenance.md), and usage/support
guidance is available in [SUPPORT.md](SUPPORT.md). Governance and maintainer responsibilities are documented in [MAINTAINERS.md](MAINTAINERS.md), and community expectations are defined in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Dependency updates are monitored with Dependabot, and CodeQL scans Python code on pull requests, default-branch changes, and a scheduled cadence.

## Contributing and security

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
development and pull-request workflow.

Please do not report suspected vulnerabilities in a public issue. Follow
[SECURITY.md](SECURITY.md) for the security reporting process.

## Production checklist

### Configuration and secrets

- [ ] No `.env`, API key, password, Hugging Face token, or private certificate is included in the source archive or image.
- [ ] All placeholder values in `.env.example` have been replaced in the server-only `.env`.
- [ ] `POSTGRES_PASSWORD` and the URL-encoded password inside `MULTIRAG_DATABASE_URL` represent the same password.
- [ ] Admin, user, and vLLM API keys are long, random, unique, and stored with restricted permissions.
- [ ] The embedding and pgvector dimensions match the selected model.

### Images, GPU, and networking

- [ ] Docker, Compose, NVIDIA driver, and NVIDIA Container Toolkit pass their checks.
- [ ] The vLLM model license/terms have been accepted and `HF_TOKEN` is read-only.
- [ ] The selected model loads within available VRAM under realistic context and concurrency.
- [ ] Floating production image tags are replaced with tested immutable digests.
- [ ] PostgreSQL and vLLM are not published to the public host network.
- [ ] Port 2011 is protected by firewall rules or a TLS reverse proxy.

### Data and operations

- [ ] PostgreSQL backup and restore have been tested.
- [ ] Uploaded-file volumes and model caches have an appropriate backup/retention policy.
- [ ] `docker compose config --quiet`, build, startup, and `deploy/healthcheck.sh` succeed on the target server.
- [ ] Upload, vectorize, search, RAG access, chat streaming, history, and deletion pass an end-to-end acceptance test.
- [ ] Logs, disk usage, container health, GPU memory, latency, and error rate are monitored.
- [ ] A tested rollback procedure and the previous image digests are available.

### Database migrations

Schema changes are versioned under `alembic/versions/`. Apply migrations
before starting a new application version:

```bash
alembic upgrade head
```

For an existing pre-migration `v0.1.0` database whose schema has been verified
to match the initial migration, back it up first and then mark the existing
schema without recreating tables:

```bash
alembic stamp 0001_initial_schema
```

Do not stamp an unknown or modified database. For production changes, test both
upgrade and rollback against a restored backup before touching the live
database.

## Delivery hygiene

Before creating a company-delivery archive, exclude generated, local, and
sensitive items:

```text
.env
.git/
.vscode/
.idea/
.venv/
venv/
__pycache__/
*.pyc
*.db
storage/
models/
logs/
```

Keep `.env.example`, source code, configuration templates, deployment files,
documentation, and the intentionally included `rag-test.txt` smoke-test sample.

## License

MultiRAG Clean is licensed under the [Apache License 2.0](LICENSE).