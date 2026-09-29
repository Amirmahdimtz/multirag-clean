from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    print(f"+ {' '.join(command)}", flush=True)
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    run(
        sys.executable,
        "-m",
        "ruff",
        "check",
        "src",
        "tests",
        "alembic",
        "main.py",
        "scripts",
    )
    run(
        sys.executable,
        "-m",
        "compileall",
        "-q",
        "src",
        "tests",
        "alembic",
        "main.py",
        "scripts",
    )
    run(
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_*.py",
        "-v",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
