# Changelog

All notable project changes should be documented in this file.

The project follows semantic versioning once tagged releases begin.

## Unreleased

### Added

- Apache-2.0 open-source licensing.
- GitHub Actions core CI.
- Unit tests for API-key authorization, configuration parsing, text splitting,
  and file storage.
- Contributor and security policies.
- GitHub issue and pull request templates.
- CodeQL code scanning.
- Dependabot configuration for Python, GitHub Actions, and Docker.
- Deterministic integration coverage for the local RAG data path.
- Maintainer roadmap, support policy, and code ownership rules.

### Changed

- README now documents the OSS workflow and project quality signals.
- Unexpected application exceptions are logged before returning a generic
  internal-server-error response.

### Planned

- versioned database migrations;
- broader integration and authorization coverage;
- first tagged release after release-readiness checks pass.
