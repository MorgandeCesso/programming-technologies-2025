from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///chat_bot.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

class Base(DeclarativeBase):
    pass
