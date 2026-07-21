import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Config:
    """Класс для хранения настроек бота"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_NAME = os.getenv('BOT_NAME')
    HF_TOKEN = os.getenv('HF_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Экземпляр для импорта
config = Config()
