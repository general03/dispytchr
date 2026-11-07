# dispytchr

[![CI](https://github.com/general03/dispytchr/actions/workflows/ci.yml/badge.svg)](https://github.com/general03/dispytchr/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)

> **Status: pre-alpha.** The project skeleton is in place; features are not implemented yet.

dispytchr captures customer requests — a form submission, an event registration... —
collects the contact's email address, stores it in a knowledge base and dispatches
follow-up actions (sending an email, syncing a CRM, ...).

It is an HTTP API built with [FastAPI](https://fastapi.tiangolo.com/) on a
**hexagonal architecture** (ports & adapters): the business core is isolated from the web
framework and the infrastructure, which plug in from the edges.

## What it does

```
  sources                      dispytchr                         actions
┌──────────────────┐   ┌──────────────────────────────┐   ┌──────────────────┐
│ form submission  │──►│ 1. capture the request       │──►│ email            │
│ event signup     │──►│ 2. extract the email address │──►│ CRM              │
│ ...              │──►│ 3. store it in the knowledge │──►│ ...              │
└──────────────────┘   │    base                      │   └──────────────────┘
                       │ 4. dispatch follow-up actions│
                       └──────────────────────────────┘
```

1. **Capture** — receive a customer request from any source (web form, event
   registration platform, ...).
2. **Collect** — extract and validate the contact's email address.
3. **Store** — insert the contact into a knowledge base, so every request is traceable
   and reusable.
4. **Dispatch** — trigger the follow-up actions configured for that request: send an
   email, create or update a contact in a CRM, and so on.

The hexagonal architecture maps directly onto this flow: each **source** is an inbound
adapter, while the **knowledge base** and each **action** (email, CRM...) are outbound
adapters behind ports. Adding a new source or a new action means writing an adapter,
without touching the business core.

## Running the API

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/general03/dispytchr.git
cd dispytchr
uv sync

uv run fastapi dev src/dispytchr/asgi.py     # development, auto-reload on :8000
uv run fastapi run src/dispytchr/asgi.py     # production mode
```

Then open:

- <http://127.0.0.1:8000/health> — liveness check
- <http://127.0.0.1:8000/docs> — interactive OpenAPI documentation (Swagger UI)
- <http://127.0.0.1:8000/redoc> — ReDoc

## Architecture

```
src/dispytchr/
├── domain/              # business model & rules — stdlib only, no I/O
│   ├── model/
│   ├── services/
│   └── errors.py
├── application/         # use cases + ports (typing.Protocol)
│   ├── ports/
│   │   ├── inbound/     # driving ports: what the app offers
│   │   └── outbound/    # driven ports: what the app needs
│   └── use_cases/
├── adapters/            # technology-specific implementations
│   ├── inbound/
│   │   └── http/        # FastAPI: app factory, routers, Pydantic schemas, error mapping
│   └── outbound/        # databases, external APIs, files...
├── bootstrap.py         # composition root: wires adapters to ports
└── asgi.py              # ASGI entrypoint: create_app(bootstrap())
```

Dependencies always point inwards. The rule is checked on every test run by
[`tests/architecture/test_dependency_rule.py`](tests/architecture/test_dependency_rule.py).
Details and rationale: [`docs/architecture.md`](docs/architecture.md) and
[ADR 0001](docs/adr/0001-hexagonal-architecture.md),
[ADR 0002](docs/adr/0002-fastapi-inbound-adapter.md).

## Development

```bash
uv sync                          # create the virtualenv with dev dependencies
uv run pre-commit install        # enable git hooks
uv run pytest                    # tests (unit, integration, architecture)
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

## Contributing

Contributions are welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md) first. To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

Distributed under the [Apache License 2.0](LICENSE).
