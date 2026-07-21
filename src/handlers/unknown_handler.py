from bot import bot

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
    bot.reply_to(
        message,
        "🤔 Я понимаю только команды из меню. Нажмите /start, чтобы начать заново."
    )