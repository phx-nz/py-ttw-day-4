"""
Main module for configuring CLI commands.

Refer to README.rst for instructions to run commands via the CLI.

:see: https://typer.tiangolo.com/tutorial/subcommands/add-typer/#put-them-together
"""
__all__ = ["app"]

import asyncio
from importlib.metadata import entry_points

import typer
import uvloop
from cli.commands import generate, profiles

# Activate uvloop for improved asyncio performance.
# :see: https://uvloop.readthedocs.io/
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Initialise the Typer application.
app = typer.Typer()

# Register commands so that they can be invoked.
app.add_typer(generate.app)
app.add_typer(profiles.app)

# Register additional commands from plugins.
for e in entry_points(group="app.command"):
    plugin: typer.Typer = e.load()

    if not isinstance(plugin, typer.Typer):
        raise TypeError(
            f"Invalid plugin {e.name} ({type(plugin).__name__}); typer.Typer expected"
        )

    app.add_typer(plugin, name=e.name)

if __name__ == "__main__":
    app()
