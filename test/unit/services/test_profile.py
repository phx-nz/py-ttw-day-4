"""
Unit tests for the profile service.
"""

from models.profile import Profile
from services.profile import ProfileService


def test_load_profiles(profiles: list[Profile]):
    """
    Sanity check, to make sure :py:func:services.profile.load_profiles works as
    expected.

    Note that the ``profiles`` fixture monkey-patches the service to load/save profiles
    in a temporary file.
    """
    loaded_profiles = ProfileService.load_profiles()
    assert loaded_profiles == profiles


def test_save_profiles():
    """
    Sanity check, to make sure :py:func:services.profile.save_profiles works as
    expected.

    Note that we declared the ``profiles`` fixture as ``autouse=True``, so it will
    run for this test even though we didn't include it in the test function parameters.
    """
    new_profiles = [
        Profile(
            id=1,
            username="orangelion962",
            password="1952",
            gender="male",
            full_name="Arlo Edwards",
            street_address="4717 Flaxmere Ave",
            email="arlo.edwards@example.com",
        ),
        Profile(
            id=2,
            username="organicwolf415",
            password="julius",
            gender="female",
            full_name="Lily Wright",
            street_address="6203 Hillsborough Road",
            email="lily.wright@example.com",
        ),
    ]

    ProfileService.save_profiles(new_profiles)

    loaded_profiles = ProfileService.load_profiles()
    assert loaded_profiles == new_profiles
