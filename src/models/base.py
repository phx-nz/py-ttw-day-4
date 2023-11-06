__all__ = ["Base"]

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    """
    Use this as the base class for ORM models.
    """

    @staticmethod
    def load_models():
        """
        Loads all the models that are exported from ``src/models/__init__.py``.

        This is used by Alembic when auto-generating migrations.
        """
        import models

        return models
