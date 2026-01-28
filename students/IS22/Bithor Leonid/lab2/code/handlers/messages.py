from utils.loader import dp
import logging
from aiogram.types import Message, ContentType
from utils.mistral import client, SYSTEM_PROMPT, TEMPERATURE
from utils.database import get_connection

@dp.message()
async def message_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO users (id, full_name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, message.from_user.full_name)
        )
        
        cur.execute(
            "INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)",
            (user_id, message.text, 'user')
        )
        
        cur.execute(
            """
            SELECT role, content 
            FROM messages 
            WHERE user_id = %s 
            ORDER BY id DESC 
            LIMIT 10
            """,
            (user_id,)
        )
        
        history = cur.fetchall()
        history.reverse()
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for role, content in history:
            messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": message.text})
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=TEMPERATURE
        )
        
        response_text = response.choices[0].message.content
        
        cur.execute(
            "INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)",
            (user_id, response_text, 'assistant')
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        await message.answer(response_text)
        
    except Exception as e:
        logging.error(f"Error in message handler: {e}")
        await message.answer("Произошла ошибка при обработке сообщения")

#@dp.message(content_types=ContentType.PHOTO)
#async def photo_handler(message: Message):
#    await message.answer("Вы отправили картинку! Пока я умею обрабатывать только текст 😊")