# Security model

This document describes the security assumptions and trust boundaries of
MultiRAG Clean. It complements `SECURITY.md`, which explains how to report a
vulnerability.

## Protected assets

The application may handle:

- API keys used for administrator and user authentication;
- uploaded documents and extracted text;
- vectorized document content and embeddings;
- user, dataset, RAG-access, chat-session, and chat-message records;
- PostgreSQL credentials and other deployment secrets;
- credentials used to reach the configured LLM service.

These values should be treated as sensitive unless the operator explicitly
decides otherwise.

## Authentication and authorization boundary

When security is enabled, protected HTTP endpoints use bearer API keys.

- admin keys have administrative access;
- user keys are bound to a single configured user ID;
- user-scoped operations must preserve ownership checks;
- RAG access is granted explicitly through the RAG-access layer.

API keys are compared with constant-time comparison. Secrets belong in runtime
configuration such as the server-side `.env`; they must not be committed to
the repository.

Disabling security is intended for local development and trusted test
environments. It must not be treated as a production-safe configuration.

## File boundary

Original upload names are reduced to a basename before persistence. Stored
files receive generated names rather than reusing a caller-controlled path.
Operators should still isolate the storage directory from unrelated host data
and apply appropriate filesystem permissions and backup policies.

## Database and vector-store boundary

The local development profile uses SQLite and a deterministic local vector
store. Production deployments use PostgreSQL/pgvector.

Changing the embedding provider, model, normalization, or vector dimension can
make existing vector data incompatible. Re-vectorization is required when the
stored embedding metadata no longer matches the active provider.

Database schema changes should not be deployed to production until a versioned
migration and rollback workflow is in place. This work is tracked publicly in
the repository roadmap/issues.

## LLM boundary

Production chat generation can be delegated to an OpenAI-compatible vLLM
service. Retrieved document text and user prompts cross that service boundary.

Operators are responsible for:

- choosing an appropriate model;
- restricting network exposure of the model endpoint;
- protecting model-service credentials;
- understanding the privacy and retention behavior of any external provider
  substituted for the local deployment.

Retrieved text and model output are untrusted data. They must not be treated as
instructions for host-level command execution or secret access.

## Container and network boundary

The provided production profile keeps PostgreSQL and vLLM on the internal
Compose network and exposes only the application port. The application image
runs as a non-root user.

Production operators should additionally enforce firewall/TLS policy, rotate
credentials, monitor logs and resource usage, and keep tested container/image
versions.

## Supply-chain controls

Repository maintenance includes:

- pull-request-only changes to the protected default branch;
- required CI and CodeQL checks;
- Dependabot update proposals;
- OpenSSF Scorecard analysis;
- tagged releases and documented release checks.

Dependency updates are reviewed rather than automatically merged.

## Out of scope

MultiRAG Clean does not itself provide:

- enterprise identity federation or SSO;
- per-request rate limiting or abuse prevention;
- encryption-key management;
- infrastructure firewalling or TLS termination;
- a sandbox for executing model-generated code.

Deployments requiring those controls should provide them at the surrounding
platform or gateway layer.
