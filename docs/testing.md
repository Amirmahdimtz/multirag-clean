# Testing strategy

MultiRAG Clean uses deterministic tests that can run without a GPU, model
download, PostgreSQL server, or external LLM service.

## Required pull-request checks

The protected `main` branch requires:

- `tests`: compilation, linting, dependency consistency checks, branch-aware
  coverage reporting, the deterministic unit/integration test suite, and
  Docker Compose configuration validation;
- `Analyze Python`: CodeQL analysis.

Pull requests cannot merge until those required checks pass.

## Unit coverage

The current unit tests cover focused behavior including:

- API-key authentication and role enforcement;
- configuration parsing;
- text splitting;
- file-storage behavior;
- user dataset ownership boundaries;
- RAG access authorization rules;
- deterministic fake embedding behavior and normalization;
- migration upgrade, drift, and downgrade behavior;
- RAG-system creation, vector-index, and embedding-compatibility invariants;
- chat session resource validation, ownership checks, and simple streaming
  persistence behavior.

## Coverage reporting

CI records branch-aware Python source coverage with `coverage.py` and prints
missing source lines in the `tests` job. Coverage is currently used as a
maintenance signal rather than a hard percentage gate: new behavior should be
covered according to risk, and the project should avoid low-value tests written
only to increase a number.

For a local coverage report:

```bash
python -m pip install "coverage[toml]>=7.6,<8"
python -m coverage run -m unittest discover -s tests -p "test_*.py" -v
python -m coverage report
```

## Deterministic integration coverage

The integration test exercises the local data path using SQLite and fake
providers:

```text
upload
  -> persist dataset
  -> process content
  -> vectorize
  -> persist embedding metadata
  -> similarity search
```

This validates cross-layer behavior without depending on external model
services.

The migration test also upgrades a fresh SQLite database to Alembic `head`,
runs `alembic check` to detect metadata drift, and downgrades back to `base`.

## Manual end-to-end path

The README documents a broader local smoke scenario that includes user
creation, dataset upload, vectorization, RAG access, chat session creation, and
NDJSON streaming.

Issue #3 tracks conversion of more of that scenario into deterministic
automated integration coverage.

## Production validation

The lightweight CI suite is not a substitute for deployment validation of the
full PostgreSQL/pgvector + Jina + vLLM stack.

Before a production release or deployment, maintainers should also validate:

- Docker Compose configuration;
- container build and startup;
- database backup/restore expectations;
- the deployment health check;
- the configured embedding/vector dimensions;
- the selected model and GPU resource profile;
- the documented end-to-end smoke path.

See [maintenance.md](maintenance.md) and
[production-deployment.md](production-deployment.md).
