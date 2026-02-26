import sys
print(sys.version)

from openai import OpenAI
from dotenv import load_dotenv
import os

# Явно указываем путь к .env файлу
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
print(f"Ищу .env по пути: {env_path}")

load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Ошибка: API ключ не найден. Проверьте .env файл.")
    exit(1)

system_prompt = os.getenv("SYSTEM_PROMPT")
if system_prompt:
    print(f"Системный промпт загружен: {system_prompt[:50]}...") 
else:
    print("Системный промпт не задан.")

client = OpenAI(
    api_key=api_key,
    base_url="https://neuroapi.host/v1"
)

def get_response(text: str, history: list, client: OpenAI) -> str:
    history.append({"role": "user", "content": text})

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history)  
    
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=1.0
    )

    answer = response.choices[0].message.content

    history.append({"role": "assistant", "content": answer})

    if len(history) > 6:
        history[:] = history[-6:]

    return answer

if __name__ == "__main__":
    history = []  
    print("Введите ваш вопрос (или 'exit' для выхода):")
    while True:
        question = input("Вы: ")
        if question.lower() == "exit":
            print("Завершение программы.")
            break
        answer = get_response(question, history, client)
        print("AI:", answer)