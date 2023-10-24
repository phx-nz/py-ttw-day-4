"""
Main module for configuring and running the API server.

Refer to README.rst for instructions to run the server.

:see: https://fastapi.tiangolo.com/tutorial/bigger-applications/
"""

from fastapi import FastAPI

from .routers import v1

__all__ = ["app"]

# Initialise the FastAPI application.
app = FastAPI()

# Activate routers to serve the API endpoints.
app.include_router(v1.router)
