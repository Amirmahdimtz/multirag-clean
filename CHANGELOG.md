# Changelog

All notable project changes should be documented in this file.

The project follows semantic versioning once tagged releases begin.

## Unreleased

### Added

- Dependency review workflow for pull requests that change dependencies.
- Authorization tests for user dataset ownership and RAG access rules.
- Maintainer governance, community conduct, and repository editor configuration.
- Issue intake links for security and support guidance.

### Planned

- versioned database migrations;
- broader integration and authorization coverage.

## [0.1.0] - 2026-09-29

### Added

- Apache-2.0 open-source licensing.
- GitHub Actions CI for compilation, unit tests, and deterministic integration tests.
- Unit tests for API-key authorization, configuration parsing, text splitting,
  and file storage.
- Deterministic integration coverage for the local RAG data path.
- Contributor, security, and support policies.
- Public roadmap and maintainer release documentation.
- GitHub issue and pull request templates.
- CODEOWNERS ownership rules.
- CodeQL code scanning.
- Dependabot configuration for Python, GitHub Actions, and Docker.
- Semantic-version tagged release automation.

### Changed

- README documents project quality, maintenance, and security signals.
- Unexpected application exceptions are logged before returning a generic
  internal-server-error response.
