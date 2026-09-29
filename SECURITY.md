# Security Policy

## Supported versions

MultiRAG Clean is pre-1.0. Security fixes are applied to the latest release
line and the default branch.

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |
| Earlier untagged snapshots | No |

Users should reproduce security reports against the latest release or current
`main` whenever practical.

## Reporting a vulnerability

Please do not open a public GitHub Issue for a suspected security vulnerability.

Use GitHub's private vulnerability reporting or security advisory flow for this
repository when available. If private reporting is not available, contact the
repository maintainer through GitHub before sharing exploit details publicly.

When reporting a vulnerability, include:

- the affected component and version or commit;
- reproducible steps or a minimal proof of concept;
- the expected security impact;
- any known mitigations.

Do not include real credentials, production data, private API keys, access
tokens, or other secrets in the report.

## Security architecture

The project's trust boundaries and deployment assumptions are documented in
[docs/security-model.md](docs/security-model.md).

## Disclosure

Please allow the maintainer reasonable time to investigate and prepare a fix
before public disclosure. Confirmed issues will be documented with appropriate
remediation guidance when a fix is available.
