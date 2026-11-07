# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project skeleton following a hexagonal architecture (domain, application, adapters, bootstrap).
- HTTP API built with FastAPI as the inbound adapter: app factory, `GET /health`,
  OpenAPI docs, domain error to HTTP mapping, ASGI entrypoint (`dispytchr.asgi:app`).
- Architecture tests enforcing the dependency rule between layers.
- Tooling: uv, ruff, mypy (strict), pytest, pre-commit, GitHub Actions CI.
- Community files: README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue and PR templates.

[Unreleased]: https://github.com/general03/dispytchr/commits/main
