__all__ = ["BaseOrmService"]

from abc import ABCMeta
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from services import DatabaseService
from services.base import BaseService


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
        Setting this to ``False`` (default) lets the application access ORM instance
        properties after the session is closed.  The trade-off is that all of this
        information has to stay loaded in memory (potentially a lot if the instance has
        lots of eagerly-loaded relations).

        If you don't need to access ORM instance properties after the transaction is
        closed, you can set ``expire_on_commit=True`` to purge those attributes after
        the session is closed and save some memory.

        If you're not sure, use the default value (:

        :see: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#session-expire
        """
        return self.db.session(expire_on_commit)
