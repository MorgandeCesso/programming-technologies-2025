import logging
from aiogram.types import Message

from utils.loader import dp
from utils.gpt import get_response
from db.session import AsyncSessionLocal
from db.crud import get_or_create_user, add_message, get_last_messages
from config import CONTEXT_LIMIT

@dp.message(lambda m: m.photo is not None)
async def photo_handler(message: Message) -> None:
    
    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session=session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Друг"
            )
            await add_message(session, user.id, "user", "[PHOTO]")

        await message.answer("Вы отправили картинку!")
    except Exception as e:
        logging.error(f"Photo handler error: {e}")
        await message.answer("Ошибка при обработке картинки")

@dp.message()
async def message_handler(message: Message) -> None:
    try:
        if not message.text:
            return

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session=session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Друг"
            )

            # 1) сохраняем сообщение пользователя
            await add_message(session, user.id, "user", message.text)

            # 2) берём контекст из БД
            history = await get_last_messages(session, user.id, CONTEXT_LIMIT)

            # 3) превращаем в формат OpenAI
            context_messages = [{"role": m.role, "content": m.content} for m in history if m.role in ("user", "assistant")]

        # 4) получаем ответ от модели (вне session тоже норм)
        answer = await get_response(user_name=user.full_name, context_messages=context_messages)

        # 5) сохраняем ответ ассистента
        async with AsyncSessionLocal() as session:
            user2 = await get_or_create_user(
                session=session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Друг"
            )
            await add_message(session, user2.id, "assistant", answer)

        await message.answer(answer)

    except Exception as e:
        logging.error(f"Message handler error: {e}")
        await message.answer("Произошла ошибка при получении ответа")
