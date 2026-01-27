import logging
from groq import AsyncGroq
from config import GROQ_API_KEY, SYSTEM_PROMPT

client = AsyncGroq(api_key=GROQ_API_KEY)

async def get_response(user_name: str, context_messages: list[dict]) -> str:
    """
    context_messages: [{"role": "user" | "assistant", "content": "..."}]
    """
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "system",
                "content": f"Имя пользователя: {user_name}. Всегда обращайся к нему по имени."
            },
            *context_messages
        ]

        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Groq error: {e}")
        return "Произошла ошибка при получении ответа от модели."
