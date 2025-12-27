from db.session import SessionLocal
from db.models import UserContext

MAX_CONTEXT = 10


def get_context(user_id: int):
    
    with SessionLocal() as session:
        return (
            session.query(UserContext)
            .filter(UserContext.user_id == user_id)
            .order_by(UserContext.timestamp.desc())
            .limit(MAX_CONTEXT)
            .all()
        )


def add_message(user_id: int, role: str, content: str):
    
    with SessionLocal() as session:
        session.add(
            UserContext(
                user_id=user_id,
                role=role,
                content=content
            )
        )
        session.commit()


def clear_context(user_id: int):
    
    with SessionLocal() as session:
        session.query(UserContext) \
            .filter(UserContext.user_id == user_id) \
            .delete()
        session.commit()
