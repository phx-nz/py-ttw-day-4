__all__ = ["BaseOrmService"]

from abc import ABCMeta
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService
from services.database import DatabaseService


class BaseOrmService(BaseService, metaclass=ABCMeta):
    """
    Extends :py:class:`BaseService` with methods designed to make it easier to work with
    ORM models.
    """

    @classmethod
    def factory(cls, database: DatabaseService = None) -> Self:
        """
        Returns an instance of the service configured for regular usage.
        """
        return cls(database)

    def __init__(self, db: DatabaseService):
        super().__init__()

        self.db: DatabaseService = db

    def session(self, expire_on_commit: bool = False) -> AsyncSession:
        """
        Convenience alias for :py:meth:`DatabaseService.session`.

        :param expire_on_commit: whether to expire ORM instances after committing them.
        :see: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#session-expire
        """
        return self.db.session(expire_on_commit)
