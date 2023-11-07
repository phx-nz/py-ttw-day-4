"""
Unit tests for the profile service.
"""
import pytest

from models.profile import Profile
from services import get_service
from services.profile import EditAwardRequest, EditProfileRequest, ProfileService


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


async def test_get_get_by_id_happy_path(
    profiles: list[Profile], service: ProfileService
):
    """
    Getting a profile by its ID.
    """
    async with service.session() as session:
        assert await service.get_by_id(session, profiles[0].id) == profiles[0]


async def test_get_by_id_non_existent(service: ProfileService):
    """
    Attempting to get a profile that doesn't exist.
    """
    async with service.session() as session:
        assert await service.get_by_id(session, 999) is None


async def test_edit_by_id_happy_path(profiles: list[Profile], service: ProfileService):
    """
    Editing a profile by its ID.
    """
    target_profile = profiles[0]

    data = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    async with service.session() as session:
        actual: Profile = await service.edit_by_id(session, target_profile.id, data)
        await session.commit()

    # ID cannot be edited.
    assert actual.id == target_profile.id
    assert actual.username == data.username
    assert actual.password == data.password
    assert actual.gender == data.gender
    assert actual.full_name == data.full_name
    assert actual.street_address == data.street_address
    assert actual.email == data.email

    # Verify that the saved profile was correctly stored in the database.
    async with service.session() as session:
        persisted: Profile = await service.get_by_id(session, target_profile.id)

    # The updated profile was saved correctly in the database.
    assert persisted == actual


async def test_edit_by_id_non_existent(
    profiles: list[Profile], service: ProfileService
):
    """
    Attempting to edit a profile that doesn't exist.
    """
    data = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    async with service.session() as session:
        assert await service.edit_by_id(session, 999, data) is None


async def test_create_profile_happy_path(
    profiles: list[Profile], service: ProfileService
):
    """
    Successfully adding a profile to the database.
    """
    data = EditProfileRequest(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )

    expected = Profile(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )
    expected.id = 4

    async with service.session() as session:
        actual: Profile = await service.create(session, data)
        await session.commit()

    # The new profile is returned.
    assert actual == expected

    # The new profile was added to the database.
    async with service.session() as session:
        assert await service.get_by_id(session, actual.id) == actual


async def test_bestow_award_happy_path(
    profiles: list[Profile], service: ProfileService
):
    """
    Successfully bestowing an award upon a profile.
    """
    target_profile: Profile = profiles[0]

    data = EditAwardRequest(title="SQLAlchemist")

    async with service.session() as session:
        actual_profile: Profile = await service.bestow_award(
            session, target_profile.id, data
        )

        assert isinstance(actual_profile, Profile)
        assert len(actual_profile.awards) == 1
        assert actual_profile.awards[0].title == data.title


async def test_bestow_award_non_existent_profile(service: ProfileService):
    """
    Attempting to bestow an award upon a non-existent profile.
    """
    data = EditAwardRequest(title="SQLAlchemist")

    async with service.session() as session:
        profile = await service.bestow_award(session, 999, data)

        assert profile is None
