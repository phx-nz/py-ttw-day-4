"""
Global fixtures accessible to all tests for this project.
"""
import asyncio

import pytest
import uvloop
from class_registry import ClassRegistryInstanceCache

from dev.services.migration import MigrationService
from models import Profile
from services import ProfileService, base, get_service
from services.config import Env

# Activate uvloop for improved asyncio performance.
# :see: https://uvloop.readthedocs.io/
# :see: https://pytest-asyncio.readthedocs.io/en/latest/how-to-guides/uvloop.html
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@pytest.fixture(name="db", autouse=True)
async def fixture_db(monkeypatch) -> None:
    """
    Sets up the database for unit tests, ensuring all the migrations get run.

    Note that this fixture has ``autouse=True``, so that it is loaded automatically,
    even if for tests that don't explicitly use it.

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
    migration_service: MigrationService = get_service(MigrationService)

    # Double-check we're pointed at the right DB configuration before doing
    # anything.
    assert migration_service.db.config.env == Env.test

    # Finally, we can run migrations (:
    # Note that we have to call it "synchronously", as pytest-asyncio doesn't work with
    # session-scoped async fixtures :shrug:
    await migration_service.create_tables_from_models()
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
    async with service.session() as session:
        session.add_all(profiles)
        await session.commit()

    yield profiles
