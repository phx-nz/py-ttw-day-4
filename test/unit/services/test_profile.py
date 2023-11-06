"""
Unit tests for the profile service.
"""
import pytest

from models.profile import Profile
from services import get_service
from services.profile import ProfileService


@pytest.fixture(name="service")
def fixture_service() -> ProfileService:
    """
    Convenience alias for the ProfileService.
    """
    yield get_service(ProfileService)


async def test_load_profiles(profiles: list[Profile], service: ProfileService):
    """
    Sanity check, to make sure :py:meth:`ProfileService.load_profiles` works as
    expected.
    """
    async with service.session() as session:
        assert await service.load_profiles(session) == profiles


async def test_save_profiles(profiles: list[Profile], service: ProfileService):
    """
    Sanity check, to make sure :py:meth:`ProfileService.save_profiles` works as
    expected.
    """
    new_profiles = [
        Profile(
            username="orangelion962",
            password="1952",
            gender="male",
            full_name="Arlo Edwards",
            street_address="4717 Flaxmere Ave",
            email="arlo.edwards@example.com",
        ),
        Profile(
            username="organicwolf415",
            password="julius",
            gender="female",
            full_name="Lily Wright",
            street_address="6203 Hillsborough Road",
            email="lily.wright@example.com",
        ),
    ]

    async with service.session() as session:
        service.save_profiles(session, new_profiles)
        await session.commit()

        assert await service.load_profiles(session) == [*profiles, *new_profiles]
