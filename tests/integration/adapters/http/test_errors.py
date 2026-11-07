import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dispytchr.adapters.inbound.http.errors import DOMAIN_ERROR_STATUS
from dispytchr.domain.errors import DomainError

pytestmark = pytest.mark.integration


def test_domain_error_is_rendered_as_422(app: FastAPI) -> None:
    @app.get("/boom")
    async def boom() -> None:
        raise DomainError("rule violated")

    with TestClient(app) as client:
        response = client.get("/boom")

    assert response.status_code == DOMAIN_ERROR_STATUS == 422
    assert response.json() == {"detail": "rule violated"}
