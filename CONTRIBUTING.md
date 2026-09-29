# Contributing to MultiRAG Clean

Thank you for considering a contribution.

## Development setup

Use Python 3.10 and create an isolated virtual environment:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For local configuration and service startup, follow the repository README.

## Tests

Run the core unit test suite from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The CI workflow also compiles the Python source tree before running these tests.

## Database migrations

When a SQLAlchemy model change affects the persistent schema:

1. update the model;
2. create or edit the corresponding revision under `alembic/versions/`;
3. run `alembic upgrade head` against a disposable database;
4. run `alembic check` and confirm that no schema drift remains;
5. document upgrade or rollback impact in the pull request.

Do not use `alembic stamp` as a substitute for a migration on a database whose
schema has not been independently verified.

## Pull requests

Keep changes focused and avoid unrelated refactors. A pull request should:

- explain the problem being solved;
- describe the implementation and any compatibility impact;
- include or update tests when behavior changes;
- update documentation when configuration, APIs, migrations, or deployment behavior changes;
- ensure dependency review passes when changing package manifests;
- avoid committing generated files, local databases, credentials, tokens, or `.env` files.

Use clear, descriptive commit messages. Prefer messages that describe the change, for example:

```text
fix: reject invalid vector dimensions
test: cover API key authorization rules
docs: document production rollback procedure
```

## Reporting bugs and proposing features

Use GitHub Issues for reproducible bugs and concrete feature proposals. Include enough context to reproduce the problem, but never include secrets, API keys, private data, or production credentials.

For security vulnerabilities, follow `SECURITY.md` instead of opening a public issue.
