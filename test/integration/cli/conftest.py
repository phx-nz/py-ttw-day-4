"""
Common fixtures used by CLI integration tests.

:see: https://docs.pytest.org/en/7.4.x/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
"""

import pytest

from cli.main import app
from cli.pytest_utils import TestCliRunner


@pytest.fixture(name="runner")
def fixture_runner() -> TestCliRunner:
    """
    Sets up a dummy CLI command runner, preloaded with commands from the app.

    :see: https://typer.tiangolo.com/tutorial/testing/
    """
    yield TestCliRunner(app)
