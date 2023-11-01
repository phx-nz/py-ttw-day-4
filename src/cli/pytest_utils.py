from typing import Any, IO, Mapping, Sequence

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner


class TestCliRunner(CliRunner):
    """
    Extends :py:class:`CliRunner` so that you can specify the Typer app at
    initialisation, rather than having to provide it every time you call ``invoke()``.
    """

    # Since this class' name starts with 'test', pytest will assume it contains unit
    # tests.  Mark it so that pytest knows it should skip this class.
    # :see: https://stackoverflow.com/a/46199666/5568265
    __test__ = False

    def __init__(self, app: Typer):
        super().__init__()
        self.app = app

    def invoke(
        self,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[Any] | None = None,
        env: Mapping[str, str] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        return super().invoke(
            self.app, args, input, env, catch_exceptions, color, **extra
        )
