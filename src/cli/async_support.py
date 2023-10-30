"""
Defines helper functions for running async commands via Typer.
"""
__all__ = ["embed_event_loop"]

import asyncio
from functools import wraps


def embed_event_loop(func):
    """
    Workaround for running async functions via Typer.

    :see: https://github.com/tiangolo/typer/issues/88#issuecomment-889486850

    .. important::

       Put this decorator **after** ``@app.command``.  Example::

          # Correct
          @app.command()
          @embed_event_loop
          def some_command():
              ...

          # Incorrect
          @embed_event_loop
          @app.command()
          def some_command():
              ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coroutine():
            return await func(*args, **kwargs)

        return asyncio.run(coroutine())

    return wrapper
