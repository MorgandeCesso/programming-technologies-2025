import os
import sqlite3
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Ты дерзкий и резкий ассистент.")

BASE_URL = "https://router.huggingface.co/v1/chat/completions"

temperature = 0.7

DB_NAME = "prompts.db"

def init_db():
    """Инициализация базы данных для хранения промптов и истории"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_prompt_to_db(name, content):
    """Сохранение промпта в базу данных"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prompts (name, content) VALUES (?, ?)', (name, content))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_prompts():
    """Получение всех сохранённых промптов"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, content FROM prompts ORDER BY created_at DESC')
    prompts = cursor.fetchall()
    conn.close()
    return prompts

def get_prompt_by_id(prompt_id):
    """Получение промпта по ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM prompts WHERE id = ?', (prompt_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_prompt(prompt_id):
    """Удаление промпта из БД"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
    conn.commit()
    conn.close()


def add_to_history(role, content):
    """Добавление сообщения в историю"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()
    
    
    clean_history()

def get_history():
    """Получение последних 6 сообщений из истории"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM history ORDER BY id DESC LIMIT 6')
    messages = cursor.fetchall()
    conn.close()
    
    
    return [{"role": role, "content": content} for role, content in reversed(messages)]

def clean_history():
    """Удаление старых сообщений, оставляя только последние 6"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM history 
        WHERE id NOT IN (
            SELECT id FROM history 
            ORDER BY id DESC 
            LIMIT 6
        )
    ''')
    conn.commit()
    conn.close()

def clear_all_history():
    """Полная очистка истории (опционально)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM history')
    conn.commit()
    conn.close()

def get_response(messages, temperature=0.7):
    """Отправка запроса в Hugging Face Router API"""
    body = {
        "model": "openai/gpt-oss-120b",
        "messages": messages,
        "temperature": temperature
    }
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    

    response = requests.post(BASE_URL, json=body, headers=headers)
    if response.status_code != 200:
        return f"Ошибка API: {response.status_code} {response.text}"

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except:
        return f"Непредвиденный ответ: {data}"

def run_chat():
    global temperature, SYSTEM_PROMPT
    

    init_db()
    
    print("=== Простой текстовый ассистент (Hugging Face Router API) ===")
    print(f"Текущий системный промпт: {SYSTEM_PROMPT}")
    print(f"Текущая temperature: {temperature}\n")
    print("Команды:")
    print("  'exit' - выход из программы")
    print("  'settemp <число>' - изменить temperature (0-1)")
    print("  'setprompt' - изменить системный промпт вручную")
    print("  'showprompt' - показать текущий системный промпт")
    print("  'saveprompt' - сохранить текущий промпт в базу данных")
    print("  'loadprompt' - загрузить промпт из базы данных")
    print("  'listprompts' - показать все сохранённые промпты")
    print("  'deleteprompt' - удалить промпт из базы данных")
    print("  'showhistory' - показать историю диалога")
    print("  'clearhistory' - очистить историю диалога")
    print()

    while True:
        user_input = input("Вы: ").strip()
        
        if user_input.lower() == "exit":
            print("Завершение программы.")
            break
            
        elif user_input.lower().startswith("settemp"):
            try:
                new_temp = float(user_input.split()[1])
                if 0 <= new_temp <= 1:
                    temperature = new_temp
                    print(f"✓ Temperature изменена на {temperature}")
                else:
                    print("✗ Введите число от 0 до 1")
            except:
                print("✗ Использование: settemp 0.7")
            continue
            
        elif user_input.lower() == "setprompt":
            new_prompt = input("Введите новый системный промпт: ").strip()
            if new_prompt:
                SYSTEM_PROMPT = new_prompt
                print(f"✓ Системный промпт изменён на: {SYSTEM_PROMPT}")
            else:
                print("✗ Промпт не может быть пустым")
            continue
            
        elif user_input.lower() == "showprompt":
            print(f"\n📝 Текущий системный промпт:")
            print(f"   {SYSTEM_PROMPT}\n")
            continue
            
        elif user_input.lower() == "saveprompt":
            print(f"\nТекущий промпт: {SYSTEM_PROMPT}")
            choice = input("Сохранить текущий промпт? (y/n, Enter = новый): ").strip().lower()
            
            if choice == 'y':
                
                prompt_to_save = SYSTEM_PROMPT
            else:
                
                prompt_to_save = input("Введите новый промпт для сохранения: ").strip()
                if not prompt_to_save:
                    print("✗ Промпт не может быть пустым")
                    continue
            
            name = input("Введите название для промпта: ").strip()
            if name:
                if save_prompt_to_db(name, prompt_to_save):
                    print(f"✓ Промпт '{name}' сохранён в базу данных")
                    print(f"  Содержание: {prompt_to_save}")
                else:
                    print(f"✗ Промпт с названием '{name}' уже существует")
            else:
                print("✗ Название не может быть пустым")
            continue
            
        elif user_input.lower() == "loadprompt":
            prompts = get_all_prompts()
            if not prompts:
                print("✗ В базе данных нет сохранённых промптов")
                continue
            
            print("\nСохранённые промпты:")
            for pid, name, content in prompts:
                preview = content[:50] + "..." if len(content) > 50 else content
                print(f"  [{pid}] {name}: {preview}")
            
            try:
                prompt_id = int(input("\nВведите ID промпта для загрузки: ").strip())
                loaded_prompt = get_prompt_by_id(prompt_id)
                if loaded_prompt:
                    SYSTEM_PROMPT = loaded_prompt
                    print(f"✓ Промпт загружен: {SYSTEM_PROMPT}")
                else:
                    print("✗ Промпт с таким ID не найден")
            except ValueError:
                print("✗ Введите корректный ID")
            continue
            
        elif user_input.lower() == "listprompts":
            prompts = get_all_prompts()
            if not prompts:
                print("✗ В базе данных нет сохранённых промптов")
            else:
                print("\nСохранённые промпты:")
                for pid, name, content in prompts:
                    print(f"\n  ID: {pid}")
                    print(f"  Название: {name}")
                    print(f"  Содержание: {content}")
            continue
            
        elif user_input.lower() == "deleteprompt":
            prompts = get_all_prompts()
            if not prompts:
                print("✗ В базе данных нет сохранённых промптов")
                continue
            
            print("\nСохранённые промпты:")
            for pid, name, content in prompts:
                preview = content[:50] + "..." if len(content) > 50 else content
                print(f"  [{pid}] {name}: {preview}")
            
            try:
                prompt_id = int(input("\nВведите ID промпта для удаления: ").strip())
                delete_prompt(prompt_id)
                print(f"✓ Промпт с ID {prompt_id} удалён")
            except ValueError:
                print("✗ Введите корректный ID")
            continue
            
        elif user_input.lower() == "showhistory":
            history_messages = get_history()
            if not history_messages:
                print("\n✗ История диалога пуста\n")
            else:
                print("\n" + "="*60)
                print("ИСТОРИЯ ДИАЛОГА (последние 6 сообщений)")
                print("="*60)
                for i, msg in enumerate(history_messages, 1):
                    role_label = "Вы" if msg['role'] == 'user' else "AI"
                    print(f"\n[{i}] {role_label}: {msg['content']}")
                print("\n" + "="*60 + "\n")
            continue
            
        elif user_input.lower() == "clearhistory":
            clear_all_history()
            print("✓ История диалога очищена")
            continue

        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        
        history_messages = get_history()
        for h in history_messages:
            messages.append(h)
        
        messages.append({"role": "user", "content": user_input})

        answer = get_response(messages, temperature)
        print("AI:", answer)

        add_to_history("user", user_input)
        add_to_history("assistant", answer)

if __name__ == "__main__":
    run_chat()
