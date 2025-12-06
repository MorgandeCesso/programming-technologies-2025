from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete
from services.database.models.user import UserBase
from services.database.models.message import MessageBase
from connection import engine
from config import PROMPT

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class DatabaseSession:
    @staticmethod
    async def get_or_create_user(tg_id: int, username: str | None, full_name: str) -> UserBase:
        async with async_session() as session:
            result = await session.execute(
                select(UserBase).where(UserBase.login == str(tg_id))
            )
            user = result.scalars().first()

            if not user:
                user = UserBase(
                    login=str(tg_id),
                    name=full_name or username or "Unknown"
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    @staticmethod
    async def get_messages_by_user_id(user_id: int) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(
                select(MessageBase)
                .where(MessageBase.user_id == user_id)
                .order_by(MessageBase.id)
            )
            messages = []
            for msg in result.scalars().all():
                messages.append({"role": msg.role, "content": msg.message})
            return messages

    @staticmethod
    async def save_message(user_id: int, role: str, content: str) -> None:
        async with async_session.begin() as session:
            msg = MessageBase(user_id=user_id, role=role, message=content)
            session.add(msg)

    @staticmethod
    async def get_user(tg_id: int) -> UserBase:
        async with async_session() as session:
            
            result = await session.execute(
                select(UserBase).where(UserBase.login == str(tg_id))
            )
            user = result.scalars().first()
            return user
        
    @staticmethod
    async def del_user_messages(user_id):
        async with async_session() as session:
            print("Deleting messages for user_id:", user_id)
            await session.execute(delete(MessageBase).where(MessageBase.user_id==user_id))
            await session.commit()