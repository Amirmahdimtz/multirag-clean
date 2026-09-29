# Roadmap

This roadmap describes maintenance priorities rather than fixed delivery dates.
Items may change as real users and contributors surface new requirements.

## Completed foundations

- versioned Alembic database migrations with CI drift validation;
- CodeQL scanning and dependency review automation;
- Dependabot, CODEOWNERS, contributor/security/support policies, and releases.

## Current priorities

### 1. Broader integration coverage

Automate the deterministic local RAG workflow with SQLite and fake providers,
including authorization and failure paths. Tracked in issue #3.

### 2. Dependency and supply-chain hygiene

Keep Python, GitHub Actions, and container dependencies current through
Dependabot and review update PRs before merging.

### 3. Security automation

Run CodeQL on pull requests, default-branch changes, and a scheduled cadence.
Continue improving validation, secret handling, authorization boundaries, and
security documentation.

### 4. Release discipline

Use semantic version tags, maintain the changelog, verify CI before releases,
and publish release notes that call out migrations or compatibility changes.

## Longer-term directions

- improve observability and structured operational logging;
- add stronger production migration and rollback validation;
- expand provider compatibility without coupling core business logic to one
  model or vector backend;
- improve contributor-facing examples and reproducible deployment profiles;
- add benchmarks only when they can be measured and reproduced consistently.

## Principles

Roadmap work should preserve the layered architecture, keep local development
possible without GPU/model downloads, avoid hard-coded secrets, and prefer
small reviewable changes over broad rewrites.
