__all__ = ["MigrationService"]

import asyncio
from typing import Self

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from models.base import Base
from services import DatabaseService
from services.base import BaseService


class MigrationService(BaseService):
    """
    Runs database migrations.

    Note that this service relies on Alembic, which is not installed for production
    builds (dev dependency).
    """

    provides = "migrations"

    @classmethod
    def factory(cls, db: DatabaseService = None) -> Self:
        return MigrationService(db)

    def __init__(self, db: DatabaseService):
        super().__init__()

        self.db: DatabaseService = db

    async def create_tables_from_models(self):
        """
        Quick & dirty way to create a database, by inspecting the existing model
        classes.  It's not as precise as running all the migrations, but it's a heck of
        a lot faster to do at the start of each test (:
        """
        async with self.db.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    def run_migrations_from_env_py(self):
        """
        Runs migrations on the database "synchronously".

        This is just a synchronous shim for :py:meth:`run_migrations`, as Alembic can
        only run migrations synchronously.

        :see: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
        """

        async def _run_migrations():
            connectable: AsyncEngine = self.db.engine

            def _run_migrations_inner(connection: Connection):
                """
                :see: :py:func:`alembic.command.upgrade`
                """
                context.configure(connection=connection, target_metadata=Base.metadata)

                with context.begin_transaction():
                    context.run_migrations()

            async with connectable.connect() as connection:
                await connection.run_sync(_run_migrations_inner)

            await connectable.dispose()

        asyncio.run(_run_migrations())

    def generate_sql(self):
        """
        Generates SQL scripts to run the migrations.

        This is also known as "offline" mode for Alembic.
        :see: https://alembic.sqlalchemy.org/en/latest/offline.html
        """
        url = self.db.config.db_connection_string
        context.configure(
            url=url,
            target_metadata=Base.metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()
