from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TEMPERATURE = os.getenv("TEMPERATURE")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")