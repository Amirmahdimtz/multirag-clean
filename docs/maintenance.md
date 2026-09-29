# Maintainer workflow

This document defines the minimum release and maintenance checks for
MultiRAG Clean.

## Pull requests

Before merge:

1. Keep the change focused and explain compatibility impact.
2. Add or update tests for behavior changes.
3. Update documentation for API, configuration, deployment, or operational
   changes.
4. Verify required CI, Ruff, and CodeQL checks; review Scorecard findings when they are relevant.
5. For persistent schema changes, verify the Alembic revision and run
   `alembic check`.
6. Confirm that no secrets, local databases, generated files, or credentials
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

## Database migrations

Every persistent schema change should be represented by an Alembic revision.
Before deployment:

1. back up the target database;
2. test `alembic upgrade head` against a restored copy;
3. verify `alembic check` reports no drift;
4. test the documented downgrade path when rollback is expected;
5. never use `alembic stamp` unless the existing schema was independently
   verified to match the revision being stamped.

The application may still call SQLAlchemy `create_all` for compatibility with
local and existing flows, but schema evolution must be carried by migrations.

## Workflow dependencies

GitHub Actions should be pinned to immutable commit SHAs with a version comment.
When Dependabot proposes an action update, review the upstream release and the
resulting SHA change before merging.

## Dependency updates

Dependabot PRs should be reviewed rather than merged automatically. For each
meaningful update, check compatibility, release notes, security impact, and
the existing test suite.

## Security

CodeQL runs on pull requests, default-branch pushes, and a scheduled cadence.
Security reports should follow `SECURITY.md` and should not be disclosed in
public issues before remediation is available.
