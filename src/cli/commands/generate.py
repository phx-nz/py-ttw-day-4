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

app = typer.Typer()

API_URL_TEMPLATE = "https://randomuser.me/api/?nat=NZ&results={count}"
DEFAULT_COUNT = 5
TARGET_PATH = Path(__file__).parent.parent.parent / "data" / "profiles.json"


def extract_profile(raw_data: dict, **extras) -> Profile:
    """
    Extracts profile data from a single object in the API response.
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
    rich_print(url)

    async with AsyncClient() as client:
        # :see: https://randomuser.me/documentation#results
        raw_profiles = (await client.get(url)).json()["results"]

    # RUG creates deeply-nested objects, so we'll need to flatten them to create a more
    # relational-database-like developer experience.
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
