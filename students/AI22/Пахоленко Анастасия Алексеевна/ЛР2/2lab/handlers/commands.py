from utils.loader import dp
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from utils.database import db 

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        
        db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            f"Я твой бот-ассистент с поддержкой контекста! \n\n"
            f"Можешь задавать мне вопросы, и я буду помнить наш разговор.\n"
            f"Чтобы сбросить историю диалога, используй /reset\n\n"
            f"Пожалуйста, помни про свой баланс на счету аккаунта в OpenAI"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")

@dp.message(Command("reset"))
async def command_reset_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        db.clear_context(user_id)
        await message.answer(
            " Контекст диалога успешно сброшен!\n"
            "Я забыл всю нашу предыдущую беседу. Можешь начать новый диалог!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer(" Произошла ошибка при сбросе контекста")
        
        
@dp.message(Command("prompt"))
async def command_prompt_handler(message: Message) -> None:
    """
    Команда для установки системного промпта.
    Использование: /prompt [текст промпта]
    """
    try:
        
        prompt_text = message.text.split('/prompt', 1)[1].strip()
        
        if not prompt_text:
            await message.answer(
                "Использование команды:\n"
                "<code>/prompt [ваш промпт]</code>\n\n"
                "Пример:\n"
                "<code>/prompt Ты - эксперт по программированию. Отвечай кратко и по делу.</code>\n\n"
                "Этот промпт будет использоваться как системное сообщение для всех твоих диалогов."
                
            )
            return
        
        user_id = message.from_user.id
        
        
        current_context = db.get_context(user_id)
        
        
        if not current_context:
            current_context = [
                {"role": "system", "content": prompt_text}
            ]
        else:
            
            system_prompt_found = False
            for i, msg in enumerate(current_context):
                if msg.get("role") == "system":
                    current_context[i] = {"role": "system", "content": prompt_text}
                    system_prompt_found = True
                    break
            
            
            if not system_prompt_found:
                current_context.insert(0, {"role": "system", "content": prompt_text})
        
        
        db.save_context(user_id, current_context)
        
        
        display_prompt = prompt_text[:100] + "..." if len(prompt_text) > 100 else prompt_text
        
        await message.answer(
            f"Системный промпт успешно установлен!\n\n"
            f"Ваш промпт:\n"
            f"<i>{display_prompt}</i>\n\n"
            f"Этот промпт будет использоваться для всех твоих последующих сообщений.\n"
            f"Чтобы сбросить промпт, используй /reset"
            
        )
        
        # Сохраняем в историю сообщений
        db.save_message(user_id, "system", f"Пользователь установил промпт: {display_prompt}")
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("❌ Произошла ошибка при установке промпта")
