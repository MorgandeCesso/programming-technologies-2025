import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key")
temperature = os.getenv("temperature")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

client = Mistral(api_key=api_key)

chat_history = []

if SYSTEM_PROMPT:
    chat_history.append({"role": "system", "content": SYSTEM_PROMPT})

def get_response(text: str, client: Mistral):
    messages = chat_history.copy() 
    
    response = client.chat.complete(
        model="mistral-tiny", 
        messages=messages,
        temperature=temperature
    )
    keepingHistory(response.choices[0].message.content, "assistant")
    return response.choices[0].message.content

def keepingHistory(Message: str, role: str):
    global chat_history
    start_index = 1 if SYSTEM_PROMPT else 0
    
    dialog_history = chat_history[start_index:]
    
    if len(dialog_history) >= 6: 
        chat_history.pop(start_index) 
    
    chat_history.append({"role": role, "content": Message})

if __name__ == "__main__":
    print("Введите ваш вопрос (или 'exit' для выхода):")
    if SYSTEM_PROMPT:
        print(f"Системный промпт: {SYSTEM_PROMPT}")
    
    while True:
        question = input("Вы: ")
        if question.lower() == "exit":
            print("Завершение программы.")
            break
        keepingHistory(question, "user")
        answer = get_response(question, client)
        print("AI:", answer)