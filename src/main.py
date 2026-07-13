import sys
import os

# Добавляем путь к текущей папке в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем хендлеры
import handlers.start_handler
import handlers.callback_handler

from bot import bot
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Главная функция запуска бота"""
    logger.info("Бот запускается...")
    
    try:
        # Выводим информацию о боте
        bot_info = bot.get_me()
        logger.info(f"Бот @{bot_info.username} успешно запущен!")
        logger.info(f"Имя бота: {bot_info.first_name}")
        
        # Запускаем бота
        bot.infinity_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()