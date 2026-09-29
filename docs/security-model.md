# Security model

This document summarizes the security boundaries that contributors and
operators should preserve when changing MultiRAG Clean.

## Authentication model

When security is enabled, protected HTTP operations use bearer API keys.

Two roles are modeled:

- **admin** keys can perform administrative operations and cross-user actions;
- **user** keys are bound to one configured user identifier and must not be
  accepted for another user's resources.

Authorization is enforced in both the API dependency layer and core business
logic. Tests cover API-key role handling, user-to-dataset ownership, and RAG
access grants.

## Security-disabled mode

The local development profile can run with:

```dotenv
MULTIRAG_SECURITY_ENABLED=false
```

This mode intentionally bypasses API-key authentication and is suitable only
for trusted local development and deterministic testing. It must not be used
for an internet-exposed or otherwise untrusted deployment because requests are
treated with administrative authority.

## Data boundaries

Uploaded datasets are persisted through the configured file-storage service.
Metadata and application entities are stored through the configured database
backend. Vectorized content is written to the selected vector store.

User-owned datasets must remain bound to their owner. Shared RAG systems use
explicit access grants. Changes that bypass these ownership or grant checks are
security-sensitive and require tests.

## Production network boundary

The supplied Docker Compose production profile keeps PostgreSQL and vLLM on the
internal application network and exposes the FastAPI application service.
Operators should place the application behind appropriate network controls and
TLS termination and should not publish database or model-server ports directly.

## Secrets

Secrets must be provided through deployment configuration and must never be
committed to the repository. This includes:

- MultiRAG API keys;
- database passwords;
- vLLM API keys;
- Hugging Face tokens;
- private certificates or credentials.

The repository contains `.env.example` only as a template. Real `.env`
files are excluded from source control.

## Dependency and supply-chain controls

Dependabot monitors supported dependency ecosystems. CodeQL analyzes Python
code on pull requests, default-branch pushes, and a scheduled cadence.

GitHub Dependency Review is tracked separately because it requires Dependency
Graph to be enabled in repository settings before the workflow can operate.

## Known security limitations

The project is pre-1.0 and should be treated as evolving software. In
particular, operators are responsible for perimeter protections such as TLS,
firewall policy, rate limiting, infrastructure monitoring, secret rotation,
database backup protection, and access to the host system.

See [SECURITY.md](../SECURITY.md) for vulnerability reporting instructions.
