import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from db.context_service import clear_context, get_context, add_message

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        clear_context(message.from_user.id)

        await message.answer(
            f"Привет, {message.from_user.full_name}!(.)(.) \n\n"
            "Я чат-бот с поддержкой контекста диалога.\n"
            "Я запоминаю наш разговор и использую его в ответах.\n\n"
            "Доступные команды:\n"
            "/prompt — задать системный промпт\n"
            "/reset — сбросить историю диалога\n\n"
            "Можешь начинать общение "
        )

    except Exception as e:
        logging.error(f"Start command error: {e}")
        await message.answer("Ошибка при запуске бота")


@router.message(Command("reset"))
async def command_reset_handler(message: Message) -> None:
    try:
        clear_context(message.from_user.id)

        await message.answer(
            "Контекст диалога сброшен.\n"
            "Я забыл нашу предыдущую беседу."
        )

    except Exception as e:
        logging.error(f"Reset command error: {e}")
        await message.answer("Ошибка при сбросе контекста")


@router.message(Command("prompt"))
async def command_prompt_handler(message: Message) -> None:
    """
    Команда /prompt
    Устанавливает системный промпт
    """
    try:
        prompt_text = message.text.replace("/prompt", "", 1).strip()

        if not prompt_text:
            await message.answer(
                "Использование:\n"
                "<code>/prompt [текст]</code>\n\n"
                "Пример:\n"
                "<code>/prompt Ты — эксперт по Python. Отвечай кратко.</code>"
            )
            return

        user_id = message.from_user.id

       
        add_message(
            user_id=user_id,
            role="system",
            content=prompt_text
        )

        await message.answer(
            "Системный промпт установлен!\n\n"
            f"<i>{prompt_text[:100]}{'...' if len(prompt_text) > 100 else ''}</i>"
        )

    except Exception as e:
        logging.error(f"Prompt command error: {e}")
        await message.answer("Ошибка при установке промпта")
