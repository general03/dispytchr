import ast
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

PACKAGE = "dispytchr"
PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / PACKAGE

ALLOWED_INTERNAL: dict[str, tuple[str, ...]] = {
    "domain": (f"{PACKAGE}.domain",),
    "application": (f"{PACKAGE}.domain", f"{PACKAGE}.application"),
}
COMPOSITION_ROOT = (f"{PACKAGE}.bootstrap", f"{PACKAGE}.asgi")
FORBIDDEN_INTERNAL: dict[str, tuple[str, ...]] = {
    "adapters.inbound": (*COMPOSITION_ROOT, f"{PACKAGE}.adapters.outbound"),
    "adapters.outbound": (*COMPOSITION_ROOT, f"{PACKAGE}.adapters.inbound"),
}
STDLIB_ONLY_LAYERS = ("domain", "application")


def module_name(path: Path, root: Path = PACKAGE_ROOT) -> str:
    parts = [root.name, *path.relative_to(root).with_suffix("").parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imported_modules(source: str, current_module: str, is_package: bool = False) -> Iterator[str]:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = current_module.split(".")
                drop = node.level - 1 if is_package else node.level
                base = ".".join(base_parts[: len(base_parts) - drop])
                module = f"{base}.{node.module}" if node.module else base
            else:
                module = node.module or ""
            yield module
            yield from (f"{module}.{alias.name}" for alias in node.names)


def _matches(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == p or module.startswith(f"{p}.") for p in prefixes)


def violations(path: Path, root: Path = PACKAGE_ROOT) -> list[str]:
    current = module_name(path, root)
    layer = ".".join(current.split(".")[1:3])
    top_layer = layer.split(".")[0]
    found: list[str] = []

    for imported in imported_modules(
        path.read_text(encoding="utf-8"), current, is_package=path.name == "__init__.py"
    ):
        top = imported.split(".")[0]
        if top == PACKAGE:
            if top_layer in ALLOWED_INTERNAL and not _matches(
                imported, ALLOWED_INTERNAL[top_layer]
            ):
                found.append(f"{current} imports {imported}")
            if layer in FORBIDDEN_INTERNAL and _matches(imported, FORBIDDEN_INTERNAL[layer]):
                found.append(f"{current} imports {imported}")
        elif top_layer in STDLIB_ONLY_LAYERS and top not in sys.stdlib_module_names:
            found.append(f"{current} imports third-party {imported}")

    return sorted(set(found))


def python_files(*layers: str) -> list[Path]:
    return sorted(p for layer in layers for p in (PACKAGE_ROOT / layer).rglob("*.py"))


CHECKED_FILES = python_files("domain", "application", "adapters")


def test_scanner_sees_every_layer() -> None:
    layers = {module_name(p).split(".")[1] for p in CHECKED_FILES}
    assert layers == {"domain", "application", "adapters"}


@pytest.mark.parametrize("path", CHECKED_FILES, ids=lambda p: module_name(p))
def test_layer_respects_dependency_rule(path: Path) -> None:
    assert violations(path) == []


@pytest.mark.parametrize(
    ("relative_path", "source", "expected"),
    [
        (
            "domain/model/x.py",
            "from dispytchr.adapters.outbound import db\n",
            "dispytchr.domain.model.x imports dispytchr.adapters.outbound",
        ),
        (
            "domain/x.py",
            "import requests\n",
            "dispytchr.domain.x imports third-party requests",
        ),
        (
            "application/use_cases/x.py",
            "from ...bootstrap import bootstrap\n",
            "dispytchr.application.use_cases.x imports dispytchr.bootstrap",
        ),
        (
            "application/ports/outbound/x.py",
            "from pydantic import BaseModel\n",
            "dispytchr.application.ports.outbound.x imports third-party pydantic",
        ),
        (
            "domain/model/x.py",
            "import typing\nif typing.TYPE_CHECKING:\n    from fastapi import Request\n",
            "dispytchr.domain.model.x imports third-party fastapi",
        ),
        (
            "adapters/inbound/x.py",
            "from dispytchr.adapters import outbound\n",
            "dispytchr.adapters.inbound.x imports dispytchr.adapters.outbound",
        ),
        (
            "adapters/inbound/http/routers/x.py",
            "from dispytchr.asgi import app\n",
            "dispytchr.adapters.inbound.http.routers.x imports dispytchr.asgi",
        ),
    ],
)
def test_scanner_detects_violations(
    tmp_path: Path, relative_path: str, source: str, expected: str
) -> None:
    root = tmp_path / PACKAGE
    file = root / relative_path
    file.parent.mkdir(parents=True)
    file.write_text(source, encoding="utf-8")

    assert expected in violations(file, root)
