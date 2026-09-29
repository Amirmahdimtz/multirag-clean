# Maintainers and governance

MultiRAG Clean currently uses a lightweight maintainer model appropriate for an
early-stage open-source project.

## Primary maintainer

- GitHub: [@Amirmahdimtz](https://github.com/Amirmahdimtz)

The primary maintainer is responsible for release decisions, security response,
repository administration, roadmap prioritization, and final merge authority.

## Decision making

Routine changes should be proposed through pull requests and evaluated on:

- correctness and test coverage;
- backward compatibility;
- security and data-handling impact;
- consistency with the layered architecture;
- operational impact on local and production deployments;
- documentation and migration requirements.

For changes that affect public APIs, persisted data, authentication,
authorization, deployment contracts, or provider interfaces, the pull request
should explicitly document compatibility and migration implications.

## Contributions

External contributors are welcome. Contribution does not automatically imply
maintainer status. Maintainer responsibilities may be expanded over time based
on sustained, high-quality contributions and demonstrated familiarity with the
project's architecture and operational requirements.

## Releases

Tagged releases are created only after required repository checks pass and the
release checklist in [docs/maintenance.md](docs/maintenance.md) is satisfied.

## Security

Security-sensitive reports follow [SECURITY.md](SECURITY.md). Public disclosure
should wait until the issue has been investigated and remediation is available
when appropriate.
