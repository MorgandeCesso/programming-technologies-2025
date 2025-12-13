from services.database.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(255), unique=True)