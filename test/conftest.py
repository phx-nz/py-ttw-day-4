"""
Global fixtures accessible to all tests for this project.
"""
from tempfile import NamedTemporaryFile

import pytest

from models.profile import Profile
from services import profile


@pytest.fixture(autouse=True)
def profiles(monkeypatch) -> list[Profile]:
    """
    Injects a known set of profiles into our "database", so that
    :py:func:`services.profile.load_profiles` returns a deterministic result.

    Note that this fixture is automatically applied to all tests in this project
    (the ``autouse=True`` part in the decorator), so that you don't have to worry about
    accidentally corrupting your database when running tests (:
    """
    fixture_profiles = [
        Profile(
            id=1,
            username="angrydog315",
            password="longjohn",
            gender="male",
            full_name="Ethan Chen",
            street_address="5723 Crawford Street",
            email="ethan.chen@example.com",
        ),
        Profile(
            id=2,
            username="goldenfrog595",
            password="1qwerty",
            gender="male",
            full_name="Lewis Martin",
            street_address="1772 Maunganui Road",
            email="lewis.martin@example.com",
        ),
        Profile(
            id=3,
            username="lazytiger234",
            password="united",
            gender="female",
            full_name="Natalie Wood",
            street_address="9920 Marshland Road",
            email="natalie.wood@example.com",
        ),
    ]

    # Create a temporary file to server as our "database" during the test.
    # https://stackoverflow.com/a/51110816/5568265
    with NamedTemporaryFile() as f:
        # Override the ``_get_data_file()`` function to instead return the path to our
        # temporary "database".
        monkeypatch.setattr(profile, "_get_data_file", lambda: f.name)

        # Populate our temporary "database" with the above profiles.
        profile.save_profiles(fixture_profiles)

        # Let the test run with the "database" now populated.
        # Once the test finishes, pytest will automatically undo all the changes made
        # during the test, so even if we run a test that changes the saved profiles, the
        # fixture will reset them before the next test starts.
        yield fixture_profiles
