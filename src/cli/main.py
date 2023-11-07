"""
Main module for configuring CLI commands.

Refer to README.rst for instructions to run commands via the CLI.

:see: https://typer.tiangolo.com/tutorial/subcommands/add-typer/#put-them-together
"""
__all__ = ["app"]

import asyncio

import typer
import uvloop

from cli.commands import generate

# Activate uvloop for improved asyncio performance.
# :see: https://uvloop.readthedocs.io/
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Initialise the Typer application.
app = typer.Typer()

# Register commands so that they can be invoked.
app.add_typer(generate.app)

if __name__ == "__main__":
    app()
