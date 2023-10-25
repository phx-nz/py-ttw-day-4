"""
Main module for configuring CLI commands.

Refer to README.rst for instructions to run commands via the CLI.

:see: https://typer.tiangolo.com/tutorial/subcommands/add-typer/#put-them-together
"""

__all__ = ["app"]

import typer

from .commands import generate_profiles

app = typer.Typer()

# Activate commands.
app.add_typer(generate_profiles.app, name="generate_profiles")

if __name__ == "__main__":
    app()
