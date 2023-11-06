"""
User profile model definition.
"""
__all__ = ["Profile", "ProfileSchema"]

from pydantic import BaseModel
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


class ProfileSchema(BaseModel):
    id: int
    username: str
    password: str
    gender: str
    full_name: str
    street_address: str
    email: str
