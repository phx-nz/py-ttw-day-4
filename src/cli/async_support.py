"""
Defines helper functions for running async commands via Typer.
"""
__all__ = ["embed_event_loop"]

import asyncio
from asyncio import iscoroutinefunction
from functools import wraps


def embed_event_loop(func):
    """
    Workaround for running async functions via Typer.

    This decorator is only needed for asynchronous functions. For convenience, it acts
    as a no-op when it decorates a synchronous functions, but to improve your code's
    readability you should probably avoid doing this (:

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
    if iscoroutinefunction(func):
        # For asynchronous functions, wrap it inside a synchronous function that runs
        # its own event loop.  The function will block until the asynchronous function
        # finishes, so it's not a good general-purpose solution.  That said, we're only
        # going to run one Typer command at a time, so the blocking call is fine here.
        @wraps(func)
        def wrapper(*args, **kwargs):
            async def coroutine():
                return await func(*args, **kwargs)

            return asyncio.run(coroutine())

        return wrapper

    # For synchronous functions, just return it unmodified.
    return func
