"""
Generates profile data using the `Random User Generator API <https://randomuser.me/>`_.

Results are stored in ``profiles.json`` in the same directory as this file.

Note that downloaded profiles will replace existing ones.
"""
import asyncio
import json
import typing
from datetime import datetime
from functools import wraps
from pathlib import Path

import typer
from httpx import AsyncClient
from rich import print as rich_print

from models.profile import Profile

API_URL_TEMPLATE = "https://randomuser.me/api/?nat=NZ&results={count}"
DEFAULT_COUNT = 5
TARGET_PATH = Path(__file__).parent / "profiles.json"


def embed_event_loop(func):
    """
    Workaround for running async functions via Typer.

    :see: https://github.com/tiangolo/typer/issues/88#issuecomment-889486850
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coroutine():
            return await func(*args, **kwargs)

        return asyncio.run(coroutine())

    return wrapper


class DatetimeAwareEncoder(json.JSONEncoder):
    """
    JSON encoder with support for datetime objects.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


@embed_event_loop
async def main(count: typing.Annotated[int, typer.Argument()] = DEFAULT_COUNT):
    """
    Entry point for generating profile data.
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

    rich_print("[green]Saving profiles...[/green]")
    with open(TARGET_PATH, "w", encoding="utf8") as f:
        json.dump(list(map(dict, profiles)), f, cls=DatetimeAwareEncoder, indent=2)

    rich_print("[green]Done![/green]")


if __name__ == "__main__":
    typer.run(main)
