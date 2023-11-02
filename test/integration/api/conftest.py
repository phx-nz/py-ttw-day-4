"""
Common fixtures used by API integration tests.

:see: https://docs.pytest.org/en/7.4.x/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(name="client")
def fixture_client():
    """
    Sets up a dummy HTTP client, preloaded with API routes from our app.

    :see: https://fastapi.tiangolo.com/tutorial/testing/
    """
    return TestClient(app)
