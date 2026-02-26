from openai import AsyncOpenAI
from config import OPENAI_API_KEY, system_prompt
import logging
from .database import save_message, get_recent_messages, init_db

init_db()

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://neuroapi.host/v1")

async def get_response(message: str, client: AsyncOpenAI, name: str, user_id: int) -> str:
    try:
        # Сохраняем сообщение пользователя
        save_message(user_id, "user", message)

        # Получаем последние 6 сообщений из истории
        history = get_recent_messages(user_id, limit=6)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "system", "content": f"Ты общаешься с пользователем по имени {name}. Обращайся к нему по имени."})
        messages.append({"role": "user", "content": message})
        messages.extend(history)
        response = await client.responses.create(
            model="gpt-4.1-nano",
            input=messages
        )
        answer = response.output_text
        save_message(user_id, "assistant", answer)
        return answer
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        print(e)
        return f"Произошла ошибка при получении ответа: {e}"
    



