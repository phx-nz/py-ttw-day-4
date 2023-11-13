from pathlib import Path

import orjson
import pytest
from click.testing import Result
from pytest_httpx import HTTPXMock

from cli.async_support import embed_event_loop
from cli.commands.generate import extract_profile
from cli.pytest_utils import TestCliRunner
from models.profile import Profile
from services import get_service
from services.profile import ProfileService


@pytest.fixture(name="mock_api_data")
def fixture_mock_api_data() -> dict:
    """
    Loads a sample response from the Random User Generator API that you can use in
    tests.

    :see: ./generate/mock_api_response.json
    """
    with open(Path(__file__).parent / "data" / "mock_api_response.json", "rb") as f:
        # Don't ``yield`` here; no need to keep the file handle open during the test.
        data = orjson.loads(f.read())

    yield data


@pytest.fixture(name="mock_api_response")
def fixture_mock_api_response(httpx_mock: HTTPXMock, mock_api_data: dict) -> dict:
    """
    Injects a mock response from the Random User Generator API, using whatever the
    :py:func:`mock_api_data` fixture returns.

    .. important::

       If a test loads this fixture but doesn't end up making any API calls, it will
       cause that test to fail.

       If you want to use the mock data in your test but won't be making API calls, use
       the :py:func:`mock_api_data` fixture instead.

    :returns: the same as :py:func:`mock_api_data`, for convenience.
    """
    # :see: https://colin-b.github.io/pytest_httpx/#add-json-response
    httpx_mock.add_response(json=mock_api_data)
    yield mock_api_data


def test_extract_profile(mock_api_data: dict):
    """
    Extracting profile data from the raw API response.
    """
    expected = Profile(
        username="purpledog816",
        password="bassman",
        gender="male",
        full_name="Arthur Wang",
        street_address="1522 Saint Aubyn Street",
        email="arthur.wang@example.com",
    )

    assert extract_profile(mock_api_data["results"][0]) == expected


def test_extract_profile_with_id(mock_api_data: dict):
    """
    Assigning an ID to an extracted profile.
    """
    expected = Profile(
        username="purpledog816",
        password="bassman",
        gender="male",
        full_name="Arthur Wang",
        street_address="1522 Saint Aubyn Street",
        email="arthur.wang@example.com",
    )
    expected.id = 42

    assert extract_profile(mock_api_data["results"][0], id=42) == expected


def test_generate_profiles_happy_path(
    mock_api_response: dict,
    profiles: list[Profile],
    runner: TestCliRunner,
):
    """
    Successfully generating and installing profiles from the API service.
    """
    result = runner.invoke(["generate", "profiles"])
    assert result.exception is None

    # This command outputs lots of stuff, but what we're really interested in is
    # confirming that it found the correct profiles in the API response.
    # Note: these values come from ``./generate/mock_api_response.json``.
    assert (
        "Welcome Arthur Wang!\n"
        "Welcome Florence Walker!\n"
        "Welcome Molly Jones!\n"
        "Welcome Jake Green!\n"
        "Welcome Nathaniel Edwards!"
    ) in result.stdout

    # ``pytest-asyncio`` runs an event loop for async test functions, which causes an
    # error when trying to run the async ``generate_profiles()`` command (can't have
    # multiple running event loops).  As a workaround we have to use the
    # ``embed_event_loop`` decorator here, so that we can keep the test function
    # synchronous and prevent ``pytest-asyncio`` from running its own event loop during
    # the test :shrug:
    @embed_event_loop
    async def verify():
        # Lastly, verify that the profiles were saved correctly to the database.
        profile_service: ProfileService = get_service(ProfileService)
        async with profile_service.session() as session:
            new_profiles = [
                extract_profile(raw_profile_data, profile_id)
                for profile_id, raw_profile_data in enumerate(
                    mock_api_response["results"], start=len(profiles) + 1
                )
            ]

            assert await profile_service.load_profiles(session) == [
                *profiles,
                *new_profiles,
            ]

    verify()


def test_generate_profiles_error(
    httpx_mock: HTTPXMock, profiles: list[Profile], runner: TestCliRunner
):
    """
    The command outputs a sensible error message when the API returns an error.
    """
    # :see: https://randomuser.me/documentation#errors
    error = "Uh oh, something has gone wrong. Please tweet us @randomapi about the issue. Thank you."
    httpx_mock.add_response(json={"error": error})

    result: Result = runner.invoke(["generate", "profiles"])
    assert isinstance(result.exception, ValueError)
    assert str(result.exception) == error
