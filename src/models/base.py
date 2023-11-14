__all__ = ["Base", "model_encoder"]

from typing import Any, Sequence

from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, ONETOMANY


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


def model_encoder(model: Any, **kwargs) -> dict:
    """
    Safely converts a model instance into a dict, so it can be JSON-encoded.

    :param model: Model instance, but for convenience will accept any value.
    :param kwargs: Additional kwargs to pass to :py:func:`jsonable_encoder`.

    :see: https://github.com/tiangolo/fastapi/discussions/9026
    :see: https://github.com/sqlalchemy/sqlalchemy/issues/9785
    """
    if isinstance(model, Base):
        mapper = inspect(model).mapper

        # Add non-relationship values.
        cleaned = {key: getattr(model, key) for key in mapper.columns.keys()}

        # Add "parent" (one-to-many) relations.
        cleaned.update(
            {
                key: [model_encoder(value) for value in getattr(model, key)]
                for key, relationship in mapper.relationships.items()
                if relationship.direction == ONETOMANY
            }
        )
    elif isinstance(model, Sequence):
        cleaned = [model_encoder(value) for value in model]
    else:
        cleaned = model

    return jsonable_encoder(cleaned, **kwargs)
