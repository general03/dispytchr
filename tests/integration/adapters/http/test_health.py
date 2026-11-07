import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import dispytchr

pytestmark = pytest.mark.integration


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": dispytchr.__version__}


def test_openapi_schema_is_served(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/health" in response.json()["paths"]


def test_asgi_entrypoint_exposes_app() -> None:
    from dispytchr.asgi import app

    assert isinstance(app, FastAPI)
