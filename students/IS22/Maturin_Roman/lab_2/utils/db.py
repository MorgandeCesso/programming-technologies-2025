from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import json

DB_PATH = "sqlite:///dialog_history.db"

# Базовый класс моделей
Base = declarative_base()

# Модель таблицы
class DialogHistory(Base):
    __tablename__ = "dialog_history"

    user_id = Column(String, primary_key=True)
    history = Column(Text, nullable=False)

# Создание engine и session
engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(bind=engine)

def create_table():
    Base.metadata.create_all(engine)

create_table()

def get_history(user_id: str) -> list:
    session = SessionLocal()
    try:
        record = session.query(DialogHistory).filter_by(user_id=user_id).first()
        if record:
            return json.loads(record.history)
        return []
    finally:
        session.close()

def save_history(user_id: str, history_actual: list) -> None:
    session = SessionLocal()
    try:
        record = session.query(DialogHistory).filter_by(user_id=user_id).first()

        if record:
            record.history = json.dumps(history_actual)
        else:
            record = DialogHistory(
                user_id=user_id,
                history=json.dumps(history_actual)
            )
            session.add(record)

        session.commit()
    finally:
        session.close()
