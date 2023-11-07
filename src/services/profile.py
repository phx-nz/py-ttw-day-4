__all__ = ["ProfileService"]

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Profile
from models.service import BaseOrmService


class ProfileService(BaseOrmService):
    """
    Use cases for working with profiles.
    """

    provides = "profile"

    @staticmethod
    async def load_profiles(session: AsyncSession) -> Sequence[Profile]:
        """
        Returns all profiles in the database, un-paginated.  Handy tool for unit tests,
        and utter disaster everywhere else (:
        """
        return (await session.scalars(select(Profile))).unique().all()

    @staticmethod
    def save_profiles(session: AsyncSession, profiles: Iterable[Profile]) -> None:
        """
        Saves profiles to the database.

        Note that this method does **not** replace existing profiles!

        .. important:: Remember to call ``session.commit()`` to commit the transaction.
        """
        session.add_all(profiles)
