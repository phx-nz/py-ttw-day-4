"""
Defines CLI command for generating profiles.
"""

import typing
from pathlib import Path

import orjson
import typer
from httpx import AsyncClient
from rich import print as rich_print

from cli.async_support import embed_event_loop
from models.profile import Profile

__all__ = ["app"]

app = typer.Typer()

API_URL_TEMPLATE = "https://randomuser.me/api/?nat=NZ&results={count}"
DEFAULT_COUNT = 5
TARGET_PATH = Path(__file__).parent.parent.parent / "data" / "profiles.json"


# Decorate as ``@app.callback`` instead of ``@app.command`` so that Typer runs it
# automatically when the user invokes the ``generate_profiles`` command.
@app.callback(invoke_without_command=True)
@embed_event_loop
async def main(count: typing.Annotated[int, typer.Argument()] = DEFAULT_COUNT):
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
        Profile(
            id=profile_id,
            username=profile["login"]["username"],
            password=profile["login"]["password"],
            gender=profile["gender"],
            full_name=f'{profile["name"]["first"]} {profile["name"]["last"]}',
            street_address=f'{profile["location"]["street"]["number"]} '
            f'{profile["location"]["street"]["name"]}',
            email=profile["email"],
            created_at=profile["registered"]["date"],
        )
        for profile_id, profile in enumerate(raw_profiles, 1)
    ]

    for profile in profiles:
        rich_print(f"[green]Welcome [cyan]{profile.full_name}[/cyan]![/green]")

    rich_print(f"[green]Saving profiles to {TARGET_PATH}...[/green]")
    with open(TARGET_PATH, "wb") as f:
        f.write(orjson.dumps(list(map(dict, profiles)), option=orjson.OPT_INDENT_2))

    rich_print("[green]Done![/green]")
