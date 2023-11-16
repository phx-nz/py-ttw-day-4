"""
Integration tests for ``POST /v1/profile``
"""
from fastapi.testclient import TestClient
from httpx import Response

from models.base import model_encoder
from models.profile import Profile
from services.profile import EditProfileRequest


def test_happy_path(client: TestClient, profiles: list[Profile]):
    """
    Creating a profile successfully.
    """
    request_body = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    expected = {
        "id": len(profiles) + 1,
        "username": "calmcat451",
        "password": "shortjane",
        "gender": "female",
        "full_name": "Ethel Chen",
        "street_address": "3775 Deerswim Lane",
        "email": "ethel.chen@example.com",
        "external_id": None,
        "awards": [],
    }

    response: Response = client.post("/v1/profile", json=model_encoder(request_body))
    assert response.status_code == 200

    # The response contains the new profile details.
    assert response.json() == expected
