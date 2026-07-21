from pydantic_core.core_schema import none_schema

from bot import bot

from services.response_generator import response_func

@bot.message_handler(func=lambda message: True)
def handle_unknown_messages(message):
    """Обработчик любых сообщений, которые не попали в другие хендлеры"""
    
    # Проверяем, не является ли сообщение командой (начинается с /)
    if message.text and message.text.startswith('/'):
        # Если это неизвестная команда
        bot.reply_to(
            message,
            f"❌ Неизвестная команда. Используйте /help для списка доступных команд."
        )
        return
    
    # Для обычных текстовых сообщений
    bot_answer = str(response_func(message.text)) if message.text is not None else \
    "🤔 Я понимаю только команды из меню. Нажмите /start, чтобы начать заново."
    
    bot.reply_to(
        message,
        bot_answer,
        # "🤔 Я понимаю только команды из меню. Нажмите /start, чтобы начать заново."
    )