"""
Integration tests for ``/v1`` (index).

:see: https://fastapi.tiangolo.com/tutorial/testing/
"""
from fastapi.testclient import TestClient


def test_index(client: TestClient):
    """
    This endpoint doesn't do very much (:

    :param client: Fixture injected by pytest.  See ``../conftest.py`` for details.
    """
    response = client.get("/v1")
    assert response.status_code == 200
    assert response.json() == {"message": "Kia ora te ao!"}
