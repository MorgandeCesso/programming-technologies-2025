from openai import AsyncOpenAI
from config import OPEN_AI_KEY, SYSTEM_PROMT
import logging

client = AsyncOpenAI(api_key=OPEN_AI_KEY)
system_promt = SYSTEM_PROMT

async def get_response(message: str, username: str, client: AsyncOpenAI, history) -> str:
    try:

        messages = [ {"role": "system", "content": system_promt.format(username=username)}]

        for msg in history:
            messages.append({"role": "user", "content": msg.message_db})
            messages.append({"role": "assistant", "content": msg.response_db})

        messages.append({"role": "user", "content": message})

        response = await client.responses.create(
            model="gpt-4.1-nano",
            input=messages
        )

        return response.output_text
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return "Произошла ошибка при получении ответа от ассисента"