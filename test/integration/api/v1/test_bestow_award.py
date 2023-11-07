"""
Unit tests for ``POST /v1/profile/{profile_id}/award``
"""
from fastapi.testclient import TestClient
from httpx import Response

from models import Profile
from models.base import model_encoder
from services import get_service
from services.profile import EditAwardRequest, ProfileService


async def test_happy_path(client: TestClient, profiles: list[Profile]):
    """
    Successfully bestowing an award upon a profile.
    """
    target_profile: Profile = profiles[0]

    request_body = EditAwardRequest(title="SQLAlchemist")

    response: Response = client.post(
        f"/v1/profile/{target_profile.id}/award",
        json=model_encoder(request_body),
    )
    assert response.status_code == 200

    profile_service: ProfileService = get_service(ProfileService)
    async with profile_service.session() as session:
        actual_profile = await profile_service.get_by_id(session, target_profile.id)

        assert len(actual_profile.awards) == 1
        assert actual_profile.awards[0].title == request_body.title

        assert response.json() == model_encoder(actual_profile)


def test_non_existent_profile(client: TestClient):
    """
    Attempting to bestow an award upon a non-existent profile.
    """
    request_body = EditAwardRequest(title="SQLAlchemist")

    response: Response = client.post(
        "/v1/profile/999/award", json=model_encoder(request_body)
    )
    assert response.status_code == 404
