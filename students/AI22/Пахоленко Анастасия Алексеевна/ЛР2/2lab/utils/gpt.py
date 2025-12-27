import logging
from openai import OpenAI

from config import OPENAI_API_KEY
from db.context_service import get_context, add_message

client = OpenAI(api_key=OPENAI_API_KEY)


def orm_context_to_messages(context):
   
    return [
        {"role": msg.role, "content": msg.content}
        for msg in context
    ]


async def get_response_with_context(message: str, user_id: int, user_name: str) -> str:
    try:
       
        orm_context = get_context(user_id) or []

        
        if not any(msg.role == "system" for msg in orm_context):
            add_message(
                user_id=user_id,
                role="system",
                content="Ты полезный ассистент."
            )
            orm_context = get_context(user_id)

       
        add_message(
            user_id=user_id,
            role="user",
            content=f"{user_name}: {message}"
        )

        
        orm_context = get_context(user_id)

        
        messages = orm_context_to_messages(orm_context)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content

    
        add_message(
            user_id=user_id,
            role="assistant",
            content=answer
        )

        return answer

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return "Произошла ошибка при обработке запроса."
