# Architecture

dispytchr follows a **hexagonal architecture** (Alistair Cockburn's *ports & adapters*).
The business core knows nothing about frameworks, databases or user interfaces; those
plug in from the outside through explicit contracts.

## Layers

```
        ┌──────────────────────── adapters ────────────────────────┐
        │  inbound (HTTP/FastAPI)           outbound (DB, APIs...) │
        │        │                                   ▲             │
        │        ▼                                   │             │
        │  ┌──────────────────── application ───────────────────┐  │
        │  │ ports.inbound ◄── use_cases ──► ports.outbound     │  │
        │  │                      │                             │  │
        │  │              ┌─────── domain ───────┐              │  │
        │  │              │ model · services ·   │              │  │
        │  │              │ errors               │              │  │
        │  │              └──────────────────────┘              │  │
        │  └────────────────────────────────────────────────────┘  │
        └──────────────────────────────────────────────────────────┘
              bootstrap.py wires everything · asgi.py serves it
```

| Layer | Responsibility | May import |
|-------|----------------|------------|
| `domain` | Entities, value objects, business rules, domain errors | stdlib, `domain` |
| `application` | Use cases; inbound ports (offered) and outbound ports (needed) | stdlib, `domain`, `application` |
| `adapters.inbound` | Translate an external stimulus (HTTP request) into a call to an inbound port | everything except the composition root and `adapters.outbound` |
| `adapters.outbound` | Implement an outbound port with a concrete technology | everything except the composition root and `adapters.inbound` |
| `bootstrap`, `asgi` | Composition root: build use cases with their adapters, then the FastAPI app | everything |

## Conventions

- **Ports are `typing.Protocol`s.** Adapters satisfy them structurally and never inherit
  from the core; mypy (strict) checks conformance at the injection point in `bootstrap.py`.
- **Ports are named after the need**, not the technology: `TaskRepository`, `Clock`,
  `Notifier` — not `SqlAlchemyRepo`.
- **Constructor injection** only: a use case receives its outbound ports in `__init__`.
  No service locator, no global state.
- **No I/O in the domain.** Time, randomness and identifiers are outbound ports too, which
  keeps the domain deterministic and trivially testable.
- **Errors**: the domain raises subclasses of `DomainError`; adapters map them to their
  own representation. In the HTTP adapter, `errors.py` turns them into status codes
  (`DomainError` → 422 by default).
- **Third-party dependencies** (FastAPI, Pydantic, drivers...) live only in adapters.

## HTTP adapter (FastAPI)

```
adapters/inbound/http/
├── app.py            # create_app(use_cases) -> FastAPI  (factory, no global state)
├── dependencies.py   # UseCasesDep: Annotated[UseCases, Depends(get_use_cases)]
├── errors.py         # DomainError -> HTTP response
├── routers/          # one APIRouter per resource
└── schemas/          # Pydantic request/response models (DTOs)
```

- `create_app` **receives** the use cases (`application.use_cases.UseCases`) instead of
  building them: the adapter never imports `bootstrap`, and tests inject fakes.
- Routers stay thin: validate input with a Pydantic schema, map it to domain objects,
  call the use case through `UseCasesDep`, map the result back to a response schema.
- Pydantic models are DTOs of the HTTP contract, not domain models: the domain keeps its
  own dataclasses so the API shape can evolve without touching business rules.
- Use FastAPI's `Depends` only for HTTP concerns (auth, pagination, the use cases
  themselves). Wiring of outbound adapters stays in `bootstrap.py`.

## Testing strategy

| Suite | Target | Doubles |
|-------|--------|---------|
| `tests/unit` | domain, use cases | in-memory fakes implementing outbound ports |
| `tests/integration` | adapters | `fastapi.testclient.TestClient` over `create_app(fakes)`; real infrastructure (or containers) for outbound adapters |
| `tests/architecture` | dependency rule | static analysis of imports with `ast` |

## Adding a feature — typical flow

1. Model the concept in `domain/model/` (with its invariants and unit tests).
2. Declare the inbound port in `application/ports/inbound/` and the outbound ports it needs
   in `application/ports/outbound/`.
3. Implement the use case in `application/use_cases/`, tested with fakes.
4. Expose the use case on `UseCases` (`application/use_cases/__init__.py`), typed with its port.
5. Implement the outbound adapters in `adapters/outbound/`, with integration tests.
6. Add the router and its schemas in `adapters/inbound/http/`, include it in `create_app`.
7. Wire everything in `bootstrap.py`.

Decisions are recorded as ADRs in [`docs/adr/`](adr/).
