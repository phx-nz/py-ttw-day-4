__all__ = ["EditAwardRequest", "EditProfileRequest", "ProfileService"]

from typing import Iterable, Sequence

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Award
from models.profile import Profile
from models.service import BaseOrmService


class EditAwardRequest(BaseModel):
    """
    DTO for editing/creating an Award.
    """

    title: str


class EditProfileRequest(BaseModel):
    """
    DTO for editing/creating a Profile.
    """

    username: str
    password: str
    gender: str
    full_name: str
    street_address: str
    email: str


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

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Profile | None:
        """
        :returns: the profile with the specified ID, or ``None`` if no such record
        exists.
        """
        return await session.get(Profile, id)

    @staticmethod
    async def get_by_external_id(
        session: AsyncSession, external_id: str
    ) -> Profile | None:
        """
        :returns: the profile with the specified external ID, or ``None`` if no such
        record exists.
        """
        return await session.scalar(
            select(Profile).where(Profile.external_id == external_id).limit(1)
        )

    @staticmethod
    async def edit_by_id(
        session: AsyncSession, id: int, data: EditProfileRequest
    ) -> Profile | None:
        """
        Modifies the profile with the specified ID, replacing its attributes from
        ``data``.

        .. important:: Remember to call ``session.commit()`` to commit the transaction.

        :returns: the model instance on success, or ``None`` if no such record exists.
        """
        profile = await ProfileService.get_by_id(session, id)

        if not profile:
            return None

        for column, new_value in dict(data).items():
            setattr(profile, column, new_value)

        return profile

    @staticmethod
    async def create(session: AsyncSession, data: EditProfileRequest) -> Profile:
        """
        Adds a new profile to the database and returns it.

        .. important:: Remember to call ``session.commit()`` to commit the transaction.
        """
        profile = Profile(**dict(data))
        session.add(profile)
        return profile

    @staticmethod
    async def bestow_award(
        session: AsyncSession, profile_id: int, data: EditAwardRequest
    ) -> Profile | None:
        """
        Bestows an award upon a profile.

        .. important:: Remember to call ``session.commit()`` to commit the transaction.

        :returns: the updated profile, or ``None`` if no such profile exists.
        """
        profile = await ProfileService.get_by_id(session, profile_id)

        if not profile:
            return None

        session.add(Award(**dict(data), profile=profile, profile_id=profile.id))
        return profile
