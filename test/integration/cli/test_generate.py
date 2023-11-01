from pathlib import Path

import orjson
import pytest
from pytest_httpx import HTTPXMock

from cli.commands.generate import extract_profile
from cli.pytest_utils import TestCliRunner
from models.profile import Profile
from services.profile import ProfileService


@pytest.fixture(name="mock_api_data")
def fixture_mock_api_data() -> dict:
    """
    Loads a sample response from the Random User Generator API that you can use in
    tests.

    :see: ./generate/mock_api_response.json
    """
    with open(Path(__file__).parent / "generate" / "mock_api_response.json", "rb") as f:
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
        id=42,
        username="purpledog816",
        password="bassman",
        gender="male",
        full_name="Arthur Wang",
        street_address="1522 Saint Aubyn Street",
        email="arthur.wang@example.com",
    )

    assert extract_profile(mock_api_data["results"][0], id=42) == expected


def test_generate_profiles_happy_path(
    mock_api_response: dict,
    runner: TestCliRunner,
):
    """
    Successfully generating and installing profiles from the API service.
    """
    result = runner.invoke(["generate", "profiles"])
    assert result.exit_code == 0

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

    # Lastly, verify that the profiles were saved correctly to the "database".
    assert ProfileService.load_profiles() == [
        extract_profile(raw_profile_data, id=profile_id)
        for profile_id, raw_profile_data in enumerate(
            mock_api_response["results"], start=1
        )
    ]
