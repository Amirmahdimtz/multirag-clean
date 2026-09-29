# Contributing to MultiRAG Clean

Thank you for considering a contribution. Participation is also subject to [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

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

## Pull requests

Keep changes focused and avoid unrelated refactors. A pull request should:

- explain the problem being solved;
- describe the implementation and any compatibility impact;
- include or update tests when behavior changes;
- update documentation when configuration, APIs, or deployment behavior changes;
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

## Governance

Maintainer responsibilities and decision-making expectations are documented in [MAINTAINERS.md](MAINTAINERS.md).
