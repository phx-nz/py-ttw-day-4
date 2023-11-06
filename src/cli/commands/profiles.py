__all__ = ["app"]

import orjson
import typer
from fastapi.encoders import jsonable_encoder

from cli.async_support import embed_event_loop
from models.profile import Profile
from services import get_service
from services.profile import EditProfileRequest, ProfileService

app = typer.Typer(name="profiles")


@app.command("get")
@embed_event_loop
async def get_profile(profile_id: int):
    """
    Retrieves the profile with the specified ID and outputs the details in JSON format.

    :raises: ValueError if no such profile exists.
    """
    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile = await profile_service.get_by_id(session, profile_id)

    if not profile:
        raise ValueError(f"No profile exists with ID {profile_id}")

    output_profile(profile)


@app.command("update")
@embed_event_loop
async def update_profile(profile_id: int, data_filepath: str):
    """
    Updates the profile with the specified ID, using the data at the specified
    filepath.

    Outputs the updated profile data on success.

    :raises: ValueError if no such profile exists.
    :raises: pydantic.ValidationError if the data are malformed.
    """
    with open(data_filepath, "rb") as f:
        data = EditProfileRequest(**orjson.loads(f.read()))

    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        updated_profile = await profile_service.edit_by_id(session, profile_id, data)

        if updated_profile:
            await session.commit()
            output_profile(updated_profile)
        else:
            raise ValueError(f"No profile exists with ID {profile_id}")


@app.command("create")
@embed_event_loop
async def create_profile(data_filepath: str):
    """
    Creates a new profile, using the data at the specified filepath.

    Outputs the new profile data on success.

    :raises: pydantic.ValidationError if the data are malformed.
    """
    with open(data_filepath, "rb") as f:
        data = EditProfileRequest(**orjson.loads(f.read()))

    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile = await profile_service.create(session, data)
        await session.commit()

    output_profile(profile)


def output_profile(profile: Profile) -> None:
    """
    Outputs profile data to stdout.
    """
    # Convert the model instance into a value that can be JSON-encoded.
    encoded_profile = jsonable_encoder(profile)

    # Finally, output the value in JSON format.
    # Note that :py:func:`orjson.dumps` returns a binary string, so we have to decode
    # it.
    print(orjson.dumps(encoded_profile, option=orjson.OPT_INDENT_2).decode("utf-8"))
