__all__ = ["DatabaseService"]

from functools import cached_property
from typing import Self

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from services.base import BaseService
from services.config import ConfigService


class DatabaseService(BaseService):
    """
    Provides methods to interact with the database at a low-ish level.
    """

    provides = "database"

    def __init__(self, config: ConfigService):
        self.config = config

    @classmethod
    def factory(cls, config: ConfigService = None) -> Self:
        """
        Returns an instance of the service configured for regular usage.
        """
        return DatabaseService(config)

    def session(self, expire_on_commit: bool = True) -> AsyncSession:
        """
        Creates a new ORM session.  Use as an async context manager, e.g.::

           service: DatabaseService = get_service(DatabaseService)
           async with service.session() as session:
               session.add(...)
               await session.commit()

        :param expire_on_commit: whether to expire ORM instances after committing them.
        :see: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#session-expire
        """
        session = self.session_factory()
        session.sync_session.expire_on_commit = expire_on_commit
        return session

    @cached_property
    def engine(self) -> AsyncEngine:
        """
        Returns the engine, used internally by SQLAlchemy to establish database
        connections.
        """
        return create_async_engine(self.config.db_connection_string)

    @cached_property
    def session_factory(self) -> async_sessionmaker:
        """
        Returns a factory for creating ORM sessions (akin to database connections, but
        designed for ORM operations).
        """
        return async_sessionmaker(self.engine)
