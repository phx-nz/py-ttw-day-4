__all__ = ["Award"]

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

# Make ``Profile`` a forward ref, to avoid circular imports.
# :see: https://stackoverflow.com/a/39757388/5568265
if TYPE_CHECKING:
    from models import Profile


class Award(Base):
    """
    A token acknowledging that the owner of a profile did something awesome.
    """

    __tablename__ = "awards"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    # :see: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#configuring-loader-strategies-at-mapping-time
    # :see: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#what-kind-of-loading-to-use
    profile: Mapped["Profile"] = relationship(back_populates="awards", lazy="joined")
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
