from pathlib import Path
from tempfile import NamedTemporaryFile

import orjson
import pytest
from click.testing import Result
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from cli.pytest_utils import TestCliRunner
from models.profile import Profile


@pytest.fixture(name="data_filepath")
def fixture_data_filepath() -> str:
    """
    Returns the path to the JSON file with data to create/update a profile.

    Saves a bit of typing / copy-pasting...though I probably ended up doing a lot more
    typing to create this fixture than I actually saved.

    There's probably an XKCD for that XD
    """
    return str(Path(__file__).parent / "data" / "updated_profile.json")


def test_get_profile_happy_path(profiles: list[Profile], runner: TestCliRunner):
    """
    Fetching data for a valid profile.
    """
    target_profile: Profile = profiles[0]

    # CLI arguments are always strings, so we have to cast ``target_profile.id``.
    result: Result = runner.invoke(["profiles", "get", str(target_profile.id)])

    # Verify that the command completed successfully.
    assert result.exception is None

    # Verify that the result is valid JSON with the correct values.
    # We don't need (nor want) to check how the JSON is formatted (e.g., indentation,
    # ordering, etc.), as that's an implementation detail.
    assert orjson.loads(result.stdout) == jsonable_encoder(target_profile)


def test_get_profile_non_existent(runner: TestCliRunner):
    """
    Attempting to fetch data for a profile that doesn't exist.
    """
    result: Result = runner.invoke(["profiles", "get", "999"])
    assert isinstance(result.exception, ValueError)
    assert "999" in str(result.exception)
    assert result.stdout == ""


def test_update_profile_happy_path(
    data_filepath: str,
    profiles: list[Profile],
    runner: TestCliRunner,
):
    """
    Updating a profile successfully.
    """
    target_profile: Profile = profiles[0]

    result: Result = runner.invoke(
        ["profiles", "update", str(target_profile.id), data_filepath]
    )

    assert result.exception is None
    assert orjson.loads(result.stdout) == {
        "id": target_profile.id,
        "username": "calmcat451",
        "password": "shortjane",
        "gender": "female",
        "full_name": "Ethel Chen",
        "street_address": "3775 Deerswim Lane",
        "email": "ethel.chen@example.com",
    }


def test_update_profile_non_existent(
    data_filepath: str, profiles: list[Profile], runner: TestCliRunner
):
    """
    Attempting to update a profile that doesn't exist.
    """
    result: Result = runner.invoke(["profiles", "update", "999", data_filepath])

    assert isinstance(result.exception, ValueError)
    assert "999" in str(result.exception)
    assert result.stdout == ""


def test_update_profile_malformed_data(
    profiles: list[Profile],
    runner: TestCliRunner,
):
    """
    Attempting to update a profile with malformed data in the JSON file.
    """
    target_profile = profiles[0]

    # Alternatively, instead of adding a file to the codebase, we can create a temporary
    # file on the fly.
    with NamedTemporaryFile("wb") as f:
        f.write(orjson.dumps({"foo": "bar", "baz": "luhrmann"}))
        f.flush()

        result: Result = runner.invoke(
            # ``f.name`` is the path to the temporary file.
            ["profiles", "update", str(target_profile.id), f.name]
        )

    assert isinstance(result.exception, ValidationError)
    assert "validation errors for EditProfileRequest" in str(result.exception)
    assert result.stdout == ""


def test_create_profile_happy_path(
    data_filepath: str,
    profiles: list[Profile],
    runner: TestCliRunner,
):
    """
    Successfully creating a new profile via the CLI.
    """
    expected = Profile(
        username="calmcat451",
        password="shortjane",
        gender="female",
        full_name="Ethel Chen",
        street_address="3775 Deerswim Lane",
        email="ethel.chen@example.com",
    )
    expected.id = 4

    result: Result = runner.invoke(["profiles", "create", data_filepath])

    assert result.exception is None
    assert orjson.loads(result.stdout) == jsonable_encoder(expected)
