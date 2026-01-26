from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_KEY')
OPEN_AI_KEY = os.getenv('OPENAI_API_KEY')
SYSTEM_PROMT = os.getenv('SYSTEM_PROMT')