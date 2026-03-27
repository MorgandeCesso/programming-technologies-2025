import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils.loader import dp
from db.session import AsyncSessionLocal
from db.crud import get_or_create_user, reset_context

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session=session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Друг"
            )

        await message.answer(
            f"Привет, <b>{user.full_name}</b>! Я бот-ассистент.\n"
            f"Пиши вопросы — отвечу.\n\n"
            f"Команды:\n"
            f"/reset-context — сбросить контекст"
        )
    except Exception as e:
        logging.error(f"Start handler error: {e}")
        await message.answer("Ошибка в /start")

@dp.message(Command("reset-context"))
async def reset_context_handler(message: Message) -> None:
    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session=session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Друг"
            )
            await reset_context(session, user.id)

        await message.answer("Контекст диалога сброшен ✅")
    except Exception as e:
        logging.error(f"Reset context error: {e}")
        await message.answer("Ошибка при сбросе контекста")
