"""
Main module for configuring CLI commands.

Refer to README.rst for instructions to run commands via the CLI.

:see: https://typer.tiangolo.com/tutorial/subcommands/add-typer/#put-them-together
"""
__all__ = ["app"]

import typer

from cli.commands import generate, profiles

app = typer.Typer()

# Register commands so that they can be invoked.
app.add_typer(generate.app)
app.add_typer(profiles.app)

if __name__ == "__main__":
    app()
