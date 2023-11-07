"""
User profile model definition.
"""
__all__ = ["Profile"]

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Profile(Base):
    """
    Information about a user, so that we can personalise the API experience for them.
    """

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    gender: Mapped[str]
    full_name: Mapped[str]
    street_address: Mapped[str]
    email: Mapped[str]
