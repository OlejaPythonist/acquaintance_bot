from sqlalchemy.orm import Mapped, mapped_column
from tgbot.database.base import Base


class Profile(Base):  # type: ignore
    __tablename__ = "Profile"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    age: Mapped[int]
    gender: Mapped[str]
    like: Mapped[str]
    city: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    photo: Mapped[str]
