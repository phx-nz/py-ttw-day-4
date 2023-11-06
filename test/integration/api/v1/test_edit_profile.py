"""
Unit tests for ``PUT /v1/profile/{profile_id}``.
"""
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from httpx import Response

from models.profile import Profile
from services.profile import EditProfileRequest


def test_happy_path(client: TestClient, profiles: list[Profile]):
    """
    Editing a profile successfully.
    """
    target_profile: Profile = profiles[0]

    request_body = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    response: Response = client.put(
        f"/v1/profile/{target_profile.id}",
        json=jsonable_encoder(request_body),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": target_profile.id,
        "username": "calmcat451",
        "password": "shortjane",
        "gender": "female",
        "full_name": "Ethel Chen",
        "street_address": "3775 Deerswim Lane",
        "email": "ethel.chen@example.com",
    }


def test_non_existent_profile(client: TestClient):
    """
    Attempting to edit a nonexistent profile.
    """
    request_body = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    response: Response = client.put(
        "/v1/profile/999", json=jsonable_encoder(request_body)
    )
    assert response.status_code == 404
