# Maintainer workflow

This document defines the minimum release and maintenance checks for
MultiRAG Clean.

## Pull requests

Before merge:

1. Keep the change focused and explain compatibility impact.
2. Add or update tests for behavior changes.
3. Update documentation for API, configuration, deployment, or operational
   changes.
4. Verify required CI and CodeQL checks.
5. Confirm that no secrets, local databases, generated files, or credentials
   are included.

## Releases

Before creating a version tag:

1. Ensure the default branch is green.
2. Review open security and regression issues.
3. Update `CHANGELOG.md`.
4. Confirm the application version in `config/config.yaml`.
5. Run the documented local smoke path.
6. Validate Docker Compose configuration for the intended deployment profile.
7. Call out database, environment-variable, and compatibility changes in
   release notes.

Use semantic version tags such as `v0.1.0`.

## Dependency updates

Dependabot PRs should be reviewed rather than merged automatically. For each
meaningful update, check compatibility, release notes, security impact, and
the existing test suite.

## Security

CodeQL runs on pull requests, default-branch pushes, and a scheduled cadence.
Security reports should follow `SECURITY.md` and should not be disclosed in
public issues before remediation is available.
