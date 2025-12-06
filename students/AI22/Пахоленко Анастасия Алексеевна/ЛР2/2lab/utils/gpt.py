from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import logging
from utils.database import db  

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты - полезный ассистент в Telegram-боте. 
Отвечай дружелюбно и информативно. 
Если не знаешь ответа, честно скажи об этом.
Используй эмодзи для более живого общения 
"""

async def get_response_with_context(message: str, user_id: int, user_name: str = None) -> str:
    try:
        
        context_messages = db.get_context(user_id)
        
        
        if not context_messages:
            context_messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        
        user_content = f"Пользователь {user_name} пишет: {message}" if user_name else message
        context_messages.append({"role": "user", "content": user_content})
        
        
        db.save_message(user_id, "user", message)
        
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context_messages[-10:],  
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_response = response.choices[0].message.content
        
        
        context_messages.append({"role": "assistant", "content": assistant_response})
        
    
        db.save_context(user_id, context_messages)
        
        
        db.save_message(user_id, "assistant", assistant_response)
        
        return assistant_response
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return "Произошла ошибка при получении ответа"


async def get_response(message: str, client: AsyncOpenAI, user_name: str = None) -> str:
    return await get_response_with_context(message, 0, user_name)  