# Contributing to dispytchr

Thanks for taking the time to contribute! This document explains how to propose a change.

## Ground rules

- Be respectful: this project follows its [Code of Conduct](CODE_OF_CONDUCT.md).
- For anything bigger than a small fix, **open an issue first** to discuss the approach.
- Security issues must **not** be reported publicly — see [SECURITY.md](SECURITY.md).

## Setting up

```bash
git clone https://github.com/<your-user>/dispytchr.git
cd dispytchr
uv sync
uv run pre-commit install
```

## Workflow

1. Create a branch from `main`: `git switch -c feat/short-description`.
2. Make your change, with tests.
3. Run the full check locally:
   ```bash
   uv run ruff check . && uv run ruff format --check .
   uv run mypy
   uv run pytest
   ```
4. Add an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) if the change is user-visible.
5. Open a pull request and fill in the template.

### Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):
`feat: …`, `fix: …`, `docs: …`, `refactor: …`, `test: …`, `chore: …`, `ci: …`.
Mark breaking changes with `!` (e.g. `feat!: …`) and a `BREAKING CHANGE:` footer.

## Architecture rules

The code follows a hexagonal architecture (see [docs/architecture.md](docs/architecture.md)).
Before opening a PR, check where your code belongs:

| You are writing…                                   | Put it in                          |
| -------------------------------------------------- | ---------------------------------- |
| A business rule, entity, value object              | `domain/`                          |
| A use case orchestrating the domain                | `application/use_cases/`           |
| A contract the app offers / needs                  | `application/ports/{inbound,outbound}/` |
| An HTTP endpoint (router + Pydantic schemas)       | `adapters/inbound/http/`           |
| Code depending on a framework, library or I/O      | `adapters/{inbound,outbound}/`     |
| Wiring adapters to use cases                       | `bootstrap.py`                     |

`domain/` and `application/` must only use the standard library. Third-party dependencies
are reserved for adapters and should preferably be declared as optional extras.
The architecture tests will fail if a layer imports something it should not.

## Testing conventions

- `tests/unit/` — domain and use cases, with in-memory fakes for outbound ports. Fast, no I/O.
- `tests/integration/` — adapters against real (or containerised) infrastructure.
- `tests/architecture/` — layer boundary checks. Do not weaken them to make a PR pass.

## Developer Certificate of Origin

By contributing, you certify that you have the right to submit your work under the
project's [Apache 2.0 license](LICENSE) ([DCO](https://developercertificate.org/)).
Please sign off your commits: `git commit -s`.
