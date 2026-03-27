from mistralai import Mistral
from config import OPENAI_API_KEY , SYSTEM_PROMPT
import logging
from utils.db import save_history, get_history

client = Mistral(api_key=OPENAI_API_KEY)

async def get_response(message: str, user_id: str, user_name: str, client: Mistral) -> str:
    history_actual = get_history(user_id)
    history_actual.append({"role": "user", "content": message})
    if len(history_actual) > 10:
        history_actual.pop(0)
    try:
        response = await client.chat.complete_async(
            model="mistral-tiny",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": "user", "content": f"Пользователя зовут {user_name}"}] + history_actual,
        )
        history_actual.append({"role": "assistant", "content": response.choices[0].message.content})
        save_history(user_id, history_actual)
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return "Произошла ошибка при получении ответа"