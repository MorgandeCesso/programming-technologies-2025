from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Message

async def get_or_create_user(session: AsyncSession, tg_id: int, full_name: str) -> User:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(tg_id=tg_id, full_name=full_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    # если имя поменялось — обновим
    if user.full_name != full_name:
        user.full_name = full_name
        await session.commit()

    return user

async def add_message(session: AsyncSession, user_id: int, role: str, content: str) -> None:
    msg = Message(user_id=user_id, role=role, content=content)
    session.add(msg)
    await session.commit()

async def get_last_messages(session: AsyncSession, user_id: int, limit: int) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    # сейчас в обратном порядке (свежие сверху) — развернём
    return list(reversed(rows))

async def reset_context(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(Message).where(Message.user_id == user_id))
    await session.commit()
