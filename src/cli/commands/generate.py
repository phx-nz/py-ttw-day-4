"""
Defines CLI command for generating profiles.
"""
__all__ = ["app"]

import typing
from pathlib import Path

import typer
from httpx import AsyncClient
from rich import print as rich_print

from cli.async_support import embed_event_loop
from models.profile import Profile
from services.profile import ProfileService

# Create a Typer instance to hold CLI commands for the ``generate`` namespace (similar
# to how we use routers in FastAPI).
app = typer.Typer(name="generate")

# A few constants that will be used by :py:func:`generate_profiles` below.
API_URL_TEMPLATE = "https://randomuser.me/api/?nat=NZ&results={count}"
DEFAULT_COUNT = 5
TARGET_PATH = Path(__file__).parent.parent.parent / "data" / "profiles.json"


# This command can be invoked by running ``pipenv run app-cli generate profiles``.
# Note that we have to use ``@embed_event_loop`` because this function is asynchronous.
# See the docstring for :py:func:`cli.async_support.embed_event_loop` for more info.
@app.command("profiles")
@embed_event_loop
async def generate_profiles(
    count: typing.Annotated[int, typer.Argument()] = DEFAULT_COUNT
):
    """
    Generates profile data using Random User Generator API (https://randomuser.me/).

    Results are stored in ``data/profiles.json``.

    Note that downloaded profiles will replace existing ones.
    """
    rich_print(f"[green]Loading [cyan]{count}[/cyan] profiles...[/green]")

    url = API_URL_TEMPLATE.format(count=count)
    rich_print(f"[grey]{url}[/grey]")

    async with AsyncClient() as client:
        response = (await client.get(url)).json()

    # :see: https://randomuser.me/documentation#errors
    if "error" in response:
        raise ValueError(response["error"])

    # :see: https://randomuser.me/documentation#results
    raw_profiles = response["results"]

    rich_print("[green]Transforming profiles...[/green]")
    profiles = [
        extract_profile(raw_profile_data, id=profile_id)
        for profile_id, raw_profile_data in enumerate(raw_profiles, start=1)
    ]

    for profile in profiles:
        rich_print(f"[green]Welcome [cyan]{profile.full_name}[/cyan]![/green]")

    rich_print(f"[green]Saving profiles to {TARGET_PATH}...[/green]")
    ProfileService.save_profiles(profiles)

    rich_print("[green]Done![/green]")


def extract_profile(raw_data: dict, **extras) -> Profile:
    """
    Random User Generator API returns deeply-nested objects, so this function flattens
    each one, in order to create a more relational-database-like developer experience.

    :param raw_data: the raw object from the API response.
    :param extras: additional values to include in the profile (i.e., ``id``).
    """
    return Profile(
        username=raw_data["login"]["username"],
        password=raw_data["login"]["password"],
        gender=raw_data["gender"],
        full_name=f'{raw_data["name"]["first"]} {raw_data["name"]["last"]}',
        street_address=f'{raw_data["location"]["street"]["number"]} '
        f'{raw_data["location"]["street"]["name"]}',
        email=raw_data["email"],
        **extras,
    )
