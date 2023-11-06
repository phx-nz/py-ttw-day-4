"""
Global fixtures accessible to all tests for this project.
"""

import pytest
from class_registry import ClassRegistryInstanceCache

from dev.services.migration import MigrationService
from models import Profile
from services import ProfileService, base, get_service
from services.config import Env


@pytest.fixture(name="db", autouse=True)
async def fixture_db(monkeypatch) -> None:
    """
    Sets up the database for unit tests, ensuring all the migrations get run.

    Note that this fixture has ``scope="session"``, so that it only gets loaded once
    during the entire test run.  It also has ``autouse=True``, so that it is loaded
    automatically, even if no test explicitly uses it.

    .. important::

       This fixture only sets up the database schema.  It does not populate the tables
       with any data!  Create separate fixtures to do this.
    """
    # Simulate running the app in test mode.
    monkeypatch.setenv("PY_ENV", "test")
    # Install a new instance cache for the service registry, so that it recreates each
    # service instance using the test configuration.
    monkeypatch.setattr(base, "registry", ClassRegistryInstanceCache(base._registry))

    # Get ready to run migrations.
    service: MigrationService = get_service(MigrationService)

    # Double-check we're pointed at the right DB configuration before doing
    # anything.
    assert service.db.config.env == Env.test

    # Finally, we can run migrations (:
    # Note that we have to call it "synchronously", as pytest-asyncio doesn't work with
    # session-scoped async fixtures :shrug:
    await service.create_tables_from_models()
    yield


@pytest.fixture(name="profiles")
async def fixture_profiles(monkeypatch) -> list[Profile]:
    """
    Injects a known set of profiles into our database.
    """
    profiles = [
        Profile(
            username="angrydog315",
            password="longjohn",
            gender="male",
            full_name="Ethan Chen",
            street_address="5723 Crawford Street",
            email="ethan.chen@example.com",
        ),
        Profile(
            username="goldenfrog595",
            password="1qwerty",
            gender="male",
            full_name="Lewis Martin",
            street_address="1772 Maunganui Road",
            email="lewis.martin@example.com",
        ),
        Profile(
            username="lazytiger234",
            password="united",
            gender="female",
            full_name="Natalie Wood",
            street_address="9920 Marshland Road",
            email="natalie.wood@example.com",
        ),
    ]

    service: ProfileService = get_service(ProfileService)
    async with service.session(expire_on_commit=False) as session:
        session.add_all(profiles)
        await session.commit()

    yield profiles
