from mistralai import Mistral
from config import MISTRAL_API_KEY, SYSTEM_PROMPT, TEMPERATURE

client = Mistral(api_key=MISTRAL_API_KEY)